# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from slugify import slugify

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
        names = {pl: pl.name for pl in self.with_context(lang=False)}
        for pl in self:
            role_name = slugify("price_" + names[pl])
            pl.role_name = role_name
            pl.discount_role_name = f"discount_{role_name}"
