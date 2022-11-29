# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductTemplate(models.Model):

    _inherit = "product.template"

    vt_groups = fields.Serialized(compute="_compute_vt_groups")

    @api.depends("veterinary_group_ids")
    def _compute_vt_groups(self):
        for product in self:
            product.vt_groups = {vg.id: vg.name for vg in product.veterinary_group_ids}
