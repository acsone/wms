# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductProduct(models.Model):

    _inherit = "product.product"

    allowed_partner_types_list = fields.Serializd(
        string="Allowed Partner Types List",
        compute="_compute_allowed_partner_types_list",
        help="Technical field. Stores all partner types allowed to access the product.",
    )

    @api.depends("categ_id")
    def _compute_allowed_partner_types_list(self):
        for product in self:
            product.allowed_partner_types_list = list(
                product.get_allowed_partner_types()
            )
