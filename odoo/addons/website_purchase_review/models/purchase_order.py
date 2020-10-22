# -*- coding: utf-8 -*-
# © 2018 Okia SPRL <Sylvain Van Hoof>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
import urllib
from datetime import datetime

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    discount_global_overwrite = fields.Float("Discount global overwrite")
    promotion_supplier_overwrite = fields.Float("Promotion supplier overwrite")
    total_lines = fields.Integer(
        "Total lines", compute="_compute_total_lines", readonly=True
    )
    total_lines_done = fields.Integer(
        "Total lines done", compute="_compute_total_lines", readonly=True
    )

    @api.multi
    def _compute_total_lines(self):
        for purchase in self:
            purchase.total_lines = len(purchase.order_line)
            purchase.total_lines_done = len(
                purchase.order_line.filtered(lambda line: line.is_confirmed_line)
            )

    @api.multi
    def open_purchase_review_url(self):
        self.ensure_one()

        if self.order_line:
            products = self.order_line.mapped("product_id").sorted(
                lambda product: product.name
            )
            url = "/purchase_review/{}/{}?products_to_order=true&reload_products=true".format(
                self.id, products[0].id
            )
        else:
            products = self.env["product.product"].search(
                [("supplier_id", "=", self.partner_id.id)], limit=1
            )
            if not products:
                raise ValidationError(_("There are no products for this supplier"))
            url = "/purchase_review/%s?reload_products=true" % self.id

        return {"type": "ir.actions.act_url", "url": url, "target": "self"}

    @api.multi
    def set_overwrite_values(self, vals):
        self.ensure_one()
        trigger_onchange = False

        discount_global = vals.get("global_discount_global")
        if discount_global:
            self.order_line.write({"discount_global": discount_global})
            self.discount_global_overwrite = discount_global
            trigger_onchange = True
        promotion_supplier = vals.get("global_promotion_supplier")
        if promotion_supplier:
            self.order_line.write({"promotion_supplier": promotion_supplier})
            self.promotion_supplier_overwrite = promotion_supplier
            trigger_onchange = True
        if trigger_onchange:
            self.order_line._onchange_price_unit()

    @api.multi
    def get_products(self):
        self.ensure_one()

        products = self.env["product.product"].search(
            [("supplier_id", "=", self.partner_id.id)], order="name"
        )

        all_products = []
        for product in products:
            all_products.append(product)
            if product.additional_product_id:
                all_products.append(product.additional_product_id)

        # Don't set empty line (qty == 0) as ordered product
        ordered_products = self.order_line.filtered(
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
                is_with_promo = seller.discount_purchase > 0
                is_without_promo = not is_with_promo

            is_in_bo = product.immediately_usable_qty < 0

            result.append(
                {
                    "id": product.id,
                    "name": product.name,
                    "display_name": product.display_name,
                    "ref": product.default_code,
                    "ordered_product": product in ordered_products,
                    "with_promo": is_with_promo,
                    "without_promo": is_without_promo,
                    "is_in_bo": is_in_bo,
                }
            )
        return result

    @api.multi
    def update_or_create_line(self, vals):
        self.ensure_one()

        for key in (
            "order_id",
            "product_id",
            "product_qty",
            "price_unit_base",
            "date_planned",
        ):
            if not vals.get(key):
                _logger.error("No value for %s" % key)
                return False

        vals["is_confirmed_line"] = True
        vals["order_id"] = int(vals["order_id"])
        vals["product_id"] = int(vals["product_id"])
        vals["product_qty"] = float(vals["product_qty"])
        vals["price_unit_base"] = float(vals["price_unit_base"])

        date_planned_str = vals["date_planned"]
        date_planned = fields.Datetime.from_string(date_planned_str)
        po_date_planned = fields.Datetime.from_string(self.date_planned)

        today_date = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
        # If the date is before today, keep the PO date
        if date_planned < today_date:
            vals["date_planned"] = fields.Datetime.to_string(po_date_planned)
        else:
            vals["date_planned"] = fields.Datetime.to_string(date_planned)

        orderpoint_min = vals.pop("orderpoint_min", 0)
        orderpoint_max = vals.pop("orderpoint_max", 0)
        orderpoint_qty_multiple = vals.pop("orderpoint_qty_multiple", 0)

        if orderpoint_min or orderpoint_max or orderpoint_qty_multiple:
            product = self.env["product.product"].browse(vals["product_id"])
            orderpoint_min = orderpoint_min and float(orderpoint_min) or 0.0
            orderpoint_max = orderpoint_max and float(orderpoint_max) or 0.0
            orderpoint_qty_multiple = (
                orderpoint_qty_multiple and float(orderpoint_qty_multiple) or 0.0
            )
            product.sudo().write(
                {
                    "orderpoint_min": orderpoint_min,
                    "orderpoint_max": orderpoint_max,
                    "orderpoint_qty_multiple": orderpoint_qty_multiple,
                }
            )

        PurchaseOrderLine = self.env["purchase.order.line"]

        existing_line = PurchaseOrderLine.search(
            [
                ("order_id", "=", vals["order_id"]),
                ("product_id", "=", vals["product_id"]),
            ],
            limit=1,
        )
        if existing_line:
            vals.pop("order_id")
            vals.pop("product_id")
            existing_line.write(vals)
            existing_line._onchange_price_unit()
        else:

            product_id = vals.pop("product_id")
            # TODO: not sure why we don't use all the values defined in `vals`
            line = PurchaseOrderLine.new(
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
            new_line = PurchaseOrderLine.create(new_vals)
            # The subtotal is not correct if we don't call this onchange.
            # Calling the onchange after 'onchange_product_id' above does
            # not give the expected result, probably because the 'create()'
            # method modifies some values.
            new_line._onchange_price_unit()
        if date_planned < today_date:
            self.date_planned = po_date_planned
        else:
            self.date_planned = date_planned

        return True

    @api.multi
    def get_url(self):
        self.ensure_one()

        vals = {
            "id": self.id,
            "view_type": "form",
            "model": "purchase.order",
            "action": self.env.ref("purchase.purchase_rfq").id,
            "menu_id": self.env.ref("purchase.menu_purchase_root").id,
        }
        return "/web#" + urllib.urlencode(vals)


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    is_confirmed_line = fields.Boolean("Confirmed line")
