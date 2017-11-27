# -*- coding: utf-8 -*-
# Copyright 2017 Sylvain Van Hoof (Okia SPRL)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    additional_move_ids = fields.Many2many('stock.move',
                                           'stock_move_additional_rel',
                                           'main_move_id',
                                           'additional_move_id',
                                           string='Additional move')

    @api.multi
    def quants_unreserve(self):
        if not self:
            return

        additional_moves = self.mapped('additional_move_ids')

        result = super(StockMove, self | additional_moves).quants_unreserve()

        if not additional_moves:
            return result

        additional_moves.action_cancel()
        additional_moves.unlink()

        return result
