# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class StockPickingWave(models.Model):

    _inherit = "stock.picking.wave"

    def assign_operator(self, operator=None):
        res = super(StockPickingWave, self).assign_operator(operator)
        self.mapped("picking_ids")._check_all_zones_launch_pickings()
        return res
