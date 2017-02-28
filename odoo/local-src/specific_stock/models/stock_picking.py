# -*- coding: utf-8 -*-
# Copyright 2016 Julien Coux (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def create_lots_for_picking(self):
        return super(StockPicking, self.with_context(
            default_life_date_allowed=True
        )).create_lots_for_picking()
