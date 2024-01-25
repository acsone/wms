# © 2018 Okia SPRL <Sylvain Van Hoof>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
import urllib
from datetime import datetime

from odoo import _, fields
from odoo.exceptions import ValidationError

from odoo.addons.purchase.models.purchase import PurchaseOrder as PurchaseOrderBase

_logger = logging.getLogger(__name__)


class PurchaseOrder(PurchaseOrderBase):

    discount_global_overwrite = fields.Float("Discount global overwrite")
    promotion_supplier_overwrite = fields.Float("Promotion supplier overwrite")
    total_lines = fields.Integer(
        "Total lines", compute="_compute_total_lines", readonly=True
    )
    total_lines_done = fields.Integer(
        "Total lines done", compute="_compute_total_lines", readonly=True
    )

    def _compute_total_lines(self):
        for purchase in self:
            purchase.total_lines = len(purchase.order_line)
            purchase.total_lines_done = len(
                purchase.order_line.filtered(lambda line: line.is_confirmed_line)
            )

    def open_purchase_order_builder_url(self):
        self.ensure_one()

        if self.order_line:
            products = self.order_line.mapped("product_id").sorted(
                lambda product: product.name
            )
            query = "products_to_order=true&reload_products=true"
            url = f"/purchase_order_builder/{self.id}/{products[0].id}?{query}"
        else:
            products = self.env["product.product"].search(
                [("supplier_id", "=", self.partner_id.id)], limit=1
            )
            if not products:
                raise ValidationError(_("There are no products for this supplier"))
            url = f"/purchase_order_builder/{self.id}?reload_products=true"

        return {"type": "ir.actions.act_url", "url": url, "target": "self"}

    def set_overwrite_values(self, vals):
        self.ensure_one()

        discount_global = vals.get("global_discount_global")
        if discount_global:
            self.order_line.write({"discount_global": discount_global})
            self.discount_global_overwrite = discount_global
        promotion_supplier = vals.get("global_promotion_supplier")
        if promotion_supplier:
            self.order_line.write({"promotion_supplier": promotion_supplier})
            self.promotion_supplier_overwrite = promotion_supplier

    def get_products(self):
        self.ensure_one()
        supplier_info = self.env["product.supplierinfo"].search(
            [("partner_id", "=", self.partner_id.id)]
        )
        products = supplier_info.mapped("product_tmpl_id.product_variant_ids")
        ordered_products = self.order_line.mapped("product_id")
        products |= ordered_products

        all_products = []
        for product in products:
            all_products.append(product)
            if product.additional_product_id:
                all_products.append(product.additional_product_id)

        # Don't set empty line (qty == 0) as ordered product
        ordered_products_with_qty = self.order_line.filtered(
            lambda line: line.product_qty
        ).mapped("product_id")
        partner = self.partner_id

        result = []
        for product in all_products:
            seller = product._select_seller(partner_id=partner)
            if not seller:
                is_with_promo = False
                is_without_promo = True
            else:
                is_with_promo = seller.discount > 0
                is_without_promo = not is_with_promo

            is_in_bo = product.immediately_usable_qty < 0

            result.append(
                {
                    "id": product.id,
                    "name": product.name,
                    "display_name": product.display_name,
                    "ref": product.default_code,
                    "is_stored_in_fridge": product.is_stored_in_fridge,
                    "ordered_product": product in ordered_products_with_qty,
                    "with_promo": is_with_promo,
                    "without_promo": is_without_promo,
                    "is_in_bo": is_in_bo,
                }
            )
        result.sort(key=lambda p: p["name"])
        return result

    def update_or_create_line(self, vals):
        self.ensure_one()

        for key in self._line_required_fields():
            if not vals.get(key):
                _logger.error("No value for %s", key)
                return False

        vals["is_confirmed_line"] = True
        vals["order_id"] = int(vals["order_id"])
        vals["product_id"] = int(vals["product_id"])
        vals["product_qty"] = float(vals["product_qty"])

        vals["price_unit"] = float(vals["price_unit"])

        date_planned_str = vals["date_planned"]
        date_planned = fields.Datetime.from_string(date_planned_str)
        po_date_planned = fields.Datetime.from_string(self.date_planned)

        today_date = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
        # If the date is before today, keep the PO date
        if date_planned < today_date:
            vals["date_planned"] = fields.Datetime.to_string(po_date_planned)
        else:
            vals["date_planned"] = fields.Datetime.to_string(date_planned)

        self._update_orderpoint(vals)

        p_id = vals.pop("packaging_ids", 0)
        u_qty = vals.pop("unit_qty", 0)
        packaging_id = int(p_id) if p_id else None
        unit_qty = int(float(u_qty)) if u_qty else None

        if packaging_id and unit_qty:
            vals.update(
                {
                    "product_packaging_id": packaging_id,
                    "product_packaging_qty": unit_qty,
                }
            )
        else:
            vals.update({"product_packaging_id": "", "product_packaging_qty": ""})

        existing_line = self.env["purchase.order.line"].search(
            [
                ("order_id", "=", vals["order_id"]),
                ("product_id", "=", vals["product_id"]),
            ],
            limit=1,
        )
        if existing_line:
            self._update_line(existing_line, vals)
        else:
            self._create_line(vals)
        if date_planned < today_date:
            self.date_planned = po_date_planned
        elif self.date_planned != fields.Datetime.to_string(date_planned):
            self.date_planned = date_planned

        return True

    def _line_required_fields(self):
        return (
            "order_id",
            "product_id",
            "product_qty",
            "price_unit",
            "date_planned",
        )

    def _update_orderpoint(self, vals):
        orderpoint_min = vals.pop("orderpoint_min", 0)
        orderpoint_max = vals.pop("orderpoint_max", 0)
        orderpoint_qty_multiple = vals.pop("orderpoint_qty_multiple", 0)

        if orderpoint_min or orderpoint_max or orderpoint_qty_multiple:
            product = self.env["product.product"].browse(vals["product_id"])
            orderpoint_min = float(orderpoint_min) if orderpoint_min else 0.0
            orderpoint_max = float(orderpoint_max) if orderpoint_max else 0.0
            orderpoint_qty_multiple = (
                float(orderpoint_qty_multiple) if orderpoint_qty_multiple else 0.0
            )
            if (
                product.reordering_min_qty != orderpoint_min
                or product.reordering_max_qty != orderpoint_max
                or product.orderpoint_qty_multiple != orderpoint_qty_multiple
            ):
                product.sudo().write(
                    {
                        "reordering_min_qty": orderpoint_min,
                        "reordering_max_qty": orderpoint_max,
                        "orderpoint_qty_multiple": orderpoint_qty_multiple,
                    }
                )

    def _update_line(self, existing_line, vals):
        vals.pop("order_id")
        vals.pop("product_id")
        existing_line.write(vals)

    def _create_line(self, vals):
        po_line = self.env["purchase.order.line"]
        product_id = vals.pop("product_id")
        # TODO: not sure why we don't use all the values defined in `vals`
        line = po_line.new(
            {
                # mandatory to make the onchange work fine w/ vendor info
                "product_id": product_id,
                "partner_id": self.partner_id,
                "order_id": vals["order_id"],
            }
        )
        line.onchange_product_id()
        new_vals = line._convert_to_write(line._cache)

        new_vals.update(vals)
        po_line.create(new_vals)

    def get_url(self):
        self.ensure_one()

        vals = {
            "id": self.id,
            "view_type": "form",
            "model": "purchase.order",
            "action": self.env.ref("purchase.purchase_rfq").id,
            "menu_id": self.env.ref("purchase.menu_purchase_root").id,
        }
        return f"/web#{urllib.parse.urlencode(vals)}"
