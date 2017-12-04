# -*- coding: utf-8 -*-
# © 2017 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockPackOperation(models.Model):
    _inherit = 'stock.pack.operation'

    additional_move = fields.Many2one(
        'stock.move',
        'Additional Product Move',
        ondelete='set null')

    @api.multi
    def unlink(self):
        moves = self.mapped('additional_move')
        res = super(StockPackOperation, self).unlink()
        if moves:
            op = moves.mapped('linked_move_operation_ids.operation_id')
            op -= self
            if op:
                op.unlink()
            moves.with_context(no_recompute=True).action_cancel()
            moves.unlink()
        return res
