# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductProduct(models.Model):

    _inherit = "product.product"

    abc_classification_profile_ids = fields.Many2many(
        "abc.classification.profile",
        compute="_compute_abc_classification_profile_ids",
        inverse=None,
        store=True,
    )

    @api.depends(
        "product_tmpl_id.picking_zone_id",
        "product_tmpl_id.is_mto_product",
        "product_tmpl_id.sale_ok",
    )
    def _compute_abc_classification_profile_ids(self):
        for record in self:
            profiles = record.product_tmpl_id.picking_zone_id.abc_classification_profile_ids.filtered(
                lambda profile, product=record: not product.is_mto_product
                or not profile.exclude_product_mto
            )
            profiles = profiles.filtered(
                lambda profile, product=record: product.sale_ok
                or not profile.exclude_non_sellable
            )
            record.abc_classification_profile_ids = profiles
