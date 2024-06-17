# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import _, api, fields

from odoo.addons.product.models.product_pricelist import Pricelist


class ProductPricelist(Pricelist):

    role_name = fields.Char(compute="_compute_role_name", store=True)
    discount_role_name = fields.Char(compute="_compute_role_name", store=True)

    _sql_constraints = [
        ("role_name_uniq", "UNIQUE(role_name)", _("Role name must be unique."))
    ]

    @api.depends("name")
    def _compute_role_name(self):
        for pl in self:
            pl.role_name = f"p{pl.id}"
            pl.discount_role_name = f"d{pl.id}"
