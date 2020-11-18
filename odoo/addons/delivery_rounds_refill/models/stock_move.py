# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class StockMove(models.Model):

    _inherit = "stock.move"

    @api.model_cr
    def init(self):
        res = super(StockMove, self).init()
        query = """
            CREATE INDEX IF NOT EXISTS
            stock_move_picking_id_state_index
            ON stock_move (picking_id, state)
        """
        self.env.cr.execute(query)
        return res
