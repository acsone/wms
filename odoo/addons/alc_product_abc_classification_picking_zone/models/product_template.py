# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductTemplate(models.Model):

    _inherit = "product.template"

    abc_classification_profile_ids = fields.Many2many(
        "abc.classification.profile",
        compute="_compute_abc_classification_profile_ids",
        inverse=None,
        store=True,
    )

    @api.depends("picking_zone_id",)
    def _compute_abc_classification_profile_ids(self):
        """
        Compute the profile from the picking_zone....

        Variants are not used here...
        """
        for rec in self:
            rec.abc_classification_profile_ids = (
                rec.picking_zone_id.abc_classification_profile_id
            )
