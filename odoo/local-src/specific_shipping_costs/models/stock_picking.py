# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import api, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def _add_delivery_cost_to_so(self):
        """Fee line for specific shipping cost is added when round is done"""
        if self.carrier_id.use_specific_cost_calculation:
            return
        return super(StockPicking, self)._add_delivery_cost_to_so()
