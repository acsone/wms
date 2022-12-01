# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductTemplate(models.Model):

    _inherit = "product.template"

    supplier_promotion_ids = fields.One2many(
        "product.supplierinfo", compute="_compute_seller_ids_subfields"
    )
    supplier_promotion_for_veterinaries_ids = fields.One2many(
        "product.supplierinfo", compute="_compute_seller_ids_subfields"
    )
    supplier_discount_ids = fields.One2many(
        "product.supplierinfo", compute="_compute_seller_ids_subfields"
    )

    @api.depends("seller_ids")
    def _compute_seller_ids_subfields(self):
        for product in self:
            current_info = product.seller_ids.filtered(lambda si: not si.is_past)
            product.supplier_promotion_ids = current_info.filtered(
                lambda a: a.is_promotion and not a.only_for_veterinaries
            )
            product.supplier_promotion_for_veterinaries_ids = current_info.filtered(
                lambda a: a.is_promotion and not a.only_for_veterinaries
            )
            product.supplier_discount_ids = current_info.filtered("is_sale_discount")
