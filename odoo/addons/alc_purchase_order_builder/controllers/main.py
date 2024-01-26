import logging
from datetime import datetime
from urllib.parse import urlencode

from dateutil.relativedelta import relativedelta

from odoo import _, fields, http
from odoo.exceptions import UserError
from odoo.http import request

from odoo.addons.web.controllers.home import Home

_logger = logging.getLogger(__name__)

FILTERS = [
    "products_to_order",
    "products_without_promo",
    "products_with_promo",
    "products_stored_in_fridge",
    "product_name",
    "next_product_id",
    "reload_products",
]


class PurchaseOrderBuilder(Home):
    @http.route(  # noqa: C901
        [
            "/purchase_order_builder/<model('purchase.order'):po>",
            "/purchase_order_builder/<model('purchase.order'):po>/"
            "<model('product.product'):product>",
        ],
        type="http",
        methods=["GET", "POST"],
        auth="user",
        website=False,
        csrf=False,
    )
    def purchase_order_builder(self, po, product=None, **kw):
        if not (product or self._product_from_po(po)):
            raise UserError(_("There are no products for this supplier"))

        po_line = po.order_line.filtered(lambda line: line.product_id == product)
        if len(po_line) > 1:
            raise UserError(_("You can only have one purchase order line by product"))

        kw_copy = kw.copy()
        params = {}
        for filter_ in FILTERS:
            value = kw_copy.pop(filter_, None)
            if value:
                params[filter_] = value
        # Pop debug key to avoid having different results with debug activated
        kw_copy.pop("debug", False)
        if kw_copy:
            po.update_or_create_line(kw_copy)
            if params.get("next_product_id"):
                url = f"/purchase_order_builder/{po.id}/{params['next_product_id']}"
            else:
                url = f"/purchase_order_builder/{po.id}"
            if params:
                url += f"?{urlencode(params)}"
            res = request.redirect(url)
        else:
            values = self._values(po, po_line, product)
            res = request.render("alc_purchase_order_builder.main_page", values)
        return res

    def _product_from_po(self, po):
        products = po.get_products()
        product = None
        if products:
            product_id = products[0]["id"]
            product = request.env["product.product"].browse(product_id)
        return product

    def _values(self, po, po_line, product):
        values = self._base_values(po, product)
        if po_line:
            date_planned_str = po_line.date_planned
            date_planned = fields.Datetime.from_string(date_planned_str)
            values.update(self._values_with_po_line(po_line, product, date_planned))
        else:
            values.update(self._values_with_seller(product, po, values))
        return values

    def _base_values(self, po, product):
        values = {
            # "session_info": json.dumps(request.env["ir.http"].session_info()),  # Not used anywhere but high bulky
            "po": po,
            "res_company": request.env.user.company_id,
            "current_product": product,
            "product_qty": 0,
            "pre_selected_packaging": 0,
            "unit_qty": 0,
            "total_weight": po.total_weight,
            "amount_untaxed": po.amount_untaxed,
            "is_confirmed_line": False,
            "is_existing_line": False,
            "return_url": po.get_url(),
        }
        if po.discount_global_overwrite:
            values["discount_global_overwrite"] = po.discount_global_overwrite

        if po.promotion_supplier_overwrite:
            values["promotion_supplier_overwrite"] = po.promotion_supplier_overwrite
        return values

    def _values_with_po_line(self, po_line, product, date_planned):
        return {
            "current_product": product,
            "product_qty": po_line.product_qty,
            "pre_selected_packaging": po_line.product_packaging_id.id,
            "unit_qty": po_line.product_packaging_qty,
            "price_unit": po_line.price_unit,
            "discount_global": po_line.discount_global,
            "promotion_supplier": po_line.promotion_supplier,
            "date_planned": fields.Date.to_string(date_planned),
            "is_existing_line": True,
            "is_confirmed_line": po_line.is_confirmed_line,
        }

    def _values_with_seller(self, product, po, values):
        seller = product._select_seller(partner_id=po.partner_id)

        # Set the price_unit unit base
        price_unit = seller.price if seller.price else 0

        # Set the date planned
        date_planned = self._date_planned(seller, po)

        # Set the discount global
        if values.get("discount_global_overwrite"):
            discount_global = values["discount_global_overwrite"]
        else:
            discount_global = po.partner_id.supplier_discount

        # Set the promotion supplier
        if values.get("promotion_supplier_overwrite"):
            promotion_supplier = values["promotion_supplier_overwrite"]
        else:
            promotion_supplier = seller.discount or 0

        return {
            "price_unit": price_unit,
            "discount_global": discount_global,
            "promotion_supplier": promotion_supplier,
            "date_planned": fields.Date.to_string(date_planned),
        }

    def _date_planned(self, seller, po):
        date_planned = datetime.now()
        if seller:
            delivery_lead_time = seller.delay
            date_planned += relativedelta(days=delivery_lead_time)
            date_planned = max([po.date_planned, date_planned])
        elif po.date_planned:
            date_planned = fields.Datetime.from_string(po.date_planned)
        return date_planned
