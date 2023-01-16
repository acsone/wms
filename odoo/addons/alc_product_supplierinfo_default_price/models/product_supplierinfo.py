# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductSupplierinfo(models.Model):

    _inherit = "product.supplierinfo"

    price = fields.Float(compute="_compute_price", readonly=False, store=True)

    @api.model
    def _get_default_line(self, supplier_partner_id, product_tmpl_id):
        if not supplier_partner_id or not product_tmpl_id:
            return self.browse()
        return self.search(
            [
                ("partner_id", "=", supplier_partner_id),
                ("product_tmpl_id", "=", product_tmpl_id),
                ("date_start", "=", False),
                ("date_end", "=", False),
            ],
            limit=1,
        )

    @api.model
    def _update_create_values_with_default_price(self, vals):
        if (
            vals.get("price")
            or not vals.get("partner_id")
            or not vals.get("product_tmpl_id")
        ):
            return vals
        default_line = self._get_default_line(
            vals["partner_id"], vals["product_tmpl_id"]
        )
        if default_line:
            vals["price"] = default_line.price
        return vals

    @api.model_create_multi
    def create(self, vals_list):
        """
        When the record is created by import, the price is not always given...

        if not takes the default one
        """
        new_vals_list = []
        for vals in vals_list:
            new_vals_list.append(self._update_create_values_with_default_price(vals))
        return super().create(new_vals_list)

    @api.depends("partner_id", "product_tmpl_id")
    def _compute_price(self):
        for rec in self:
            if rec.price or not rec.partner_id or not rec.product_tmpl_id:
                continue
            default_line = self._get_default_line(
                rec.partner_id.id, rec.product_tmpl_id.id
            )
            if default_line:
                rec.price = default_line.price
