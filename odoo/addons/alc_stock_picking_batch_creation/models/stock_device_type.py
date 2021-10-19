# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockDeviceType(models.Model):

    _inherit = "stock.device.type"

    min_volume_liter = fields.Float()
    max_volume_liter = fields.Float()
    min_volume = fields.Float(compute="_compute_min_volume")
    max_volume = fields.Float(compute="_compute_max_volume")

    @api.depends("min_volume_liter")
    def _compute_min_volume(self):
        for rec in self:
            rec.min_volume = rec.min_volume_liter / 1000.0

    @api.depends("max_volume_liter")
    def _compute_max_volume(self):
        for rec in self:
            rec.max_volume = rec.max_volume_liter / 1000.0
