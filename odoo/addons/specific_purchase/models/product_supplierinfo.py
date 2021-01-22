# -*- coding: utf-8 -*-
from odoo import _, api, fields, models


class ProductSupplierinfo(models.Model):
    _inherit = "product.supplierinfo"

    product_cnk_code = fields.Char(related="product_tmpl_id.cnk_code", readonly=True)

    @api.onchange("name")
    def onchange_name(self):
        if not self.name.delivery_lead_time:
            return

        delay = self.name.delivery_lead_time
        self.delay = delay

        if self.name and self.product_tmpl_id:
            self._onchange_update_price_and_ref()

    @api.onchange("product_tmpl_id")
    def onchange_product_tmpl_id(self):
        if self.name and self.product_tmpl_id:
            self._onchange_update_price_and_ref()

    def _onchange_update_price_and_ref(self):
        base_info = self.search(
            [
                ("name", "=", self.name.id),
                ("product_tmpl_id", "=", self.product_tmpl_id.id),
            ],
            limit=1,
            order="min_qty ASC",
        )
        if base_info:
            self.update(
                {"price": base_info.price, "product_code": base_info.product_code}
            )

    @api.multi
    def open_form_view(self):
        self.ensure_one()
        view = self.env.ref("specific_purchase.product_supplierinfo_view_form")

        return {
            "name": _("Supplier info"),
            "view_type": "form",
            "view_mode": "form",
            "view_id": view.id,
            "res_model": self._name,
            "type": "ir.actions.act_window",
            "target": "current",
            "res_id": self.id,
            "context": self.env.context,
        }

    @api.model
    def create(self, values):
        """ This extension of create() allows to import supplier infos with
        either CNK code (from product template) or product_code (from other
        supplierinfo to get product template) instead of product template.
        If both CNK code and product code are in values, the CNK code will be
        used to search the product.
        """
        vals_cnk = values.get("product_cnk_code")
        vals_prod_tmpl = values.get("product_tmpl_id")
        vals_prod_code = values.get("product_code")
        cnk_product_tmpl = False
        code_product_tmpl = False
        if vals_cnk and not vals_prod_tmpl:
            cnk_product_tmpl = self.env["product.template"].search(
                [("cnk_code", "=", vals_cnk)]
            )
            values.pop("product_cnk_code")
        if vals_prod_code and not vals_prod_tmpl:
            code_product_supplierinfo = self.search(
                [("product_code", "=", vals_prod_code)], limit=1
            )
            code_product_tmpl = code_product_supplierinfo.product_tmpl_id
        if cnk_product_tmpl or code_product_tmpl:
            prod_id = (
                cnk_product_tmpl
                and cnk_product_tmpl.id
                or code_product_tmpl
                and code_product_tmpl.id
            )
            values.update({"product_tmpl_id": prod_id})
        new_info = super(ProductSupplierinfo, self).create(values)
        new_info._onchange_update_price_and_ref()
        return new_info
