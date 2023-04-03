# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields

from odoo.addons.alc_product_supplierinfo_default_price.models.product_supplierinfo import (
    ProductSupplierinfo as ProductSupplierinfoBase,
)


class ProductSupplierinfo(ProductSupplierinfoBase):

    product_cnk_code = fields.Char(related="product_tmpl_id.cnk_code", readonly=True)

    @api.onchange("product_id", "partner_id")
    def _onchange_update_product_code(self):
        for rec in self:
            rec.product_code = self._get_default_line(
                rec.partner_id.id, rec.product_id.product_tmpl_id.id
            ).product_code

    @api.model_create_multi
    def create(self, vals_list):
        """This extension of create() allows to import supplier infos with.

        either CNK code (from product template) or product_code (from other
        supplierinfo to get product template) instead of product template.
        If both CNK code and product code are in values, the CNK code will be
        used to search the product.
        """
        for vals in vals_list:
            vals_cnk = vals.get("product_cnk_code")
            vals_prod_tmpl = vals.get("product_tmpl_id")
            vals_prod_code = vals.get("product_code")
            cnk_product_tmpl = False
            code_product_tmpl = False
            if vals_cnk and not vals_prod_tmpl:
                cnk_product_tmpl = self.env["product.template"].search(
                    [("cnk_code", "=", vals_cnk)]
                )
                vals.pop("product_cnk_code")
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
                vals.update({"product_tmpl_id": prod_id})
            if (
                not vals.get("product_code")
                and "partner_id" in vals
                and "product_tmpl_id" in vals
            ):
                vals["product_code"] = self._get_default_line(
                    vals["partner_id"], vals["product_tmpl_id"]
                ).product_code
        return super().create(vals_list)
