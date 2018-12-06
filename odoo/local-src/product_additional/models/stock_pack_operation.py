# -*- coding: utf-8 -*-
# Copyright 2017-2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

import logging
_logger = logging.getLogger(__name__)


class StockPackOperation(models.Model):
    _inherit = 'stock.pack.operation'

    additional_move_id = fields.Many2one(
        'stock.move',
        'Additional Product Move',
        ondelete='set null',
        old='additional_move')

    @api.multi
    def unlink(self):
        if self.env.context.get('skip_additional'):
            return super(StockPackOperation, self).unlink()

        for additional_move in self.mapped('additional_move_id'):
            ops = additional_move.mapped(
                'linked_move_operation_ids.operation_id')
            ops_done = ops.filtered('qty_done')
            # If a quantity has been already set on the pack op. Keep it.
            # Another one will come back if the main move is reassigned
            # but we don't want to loose what was done.
            if not ops_done:
                super(StockPackOperation, ops).unlink()
                ops_moves = ops.mapped('linked_move_operation_ids.move_id')
                _logger.debug("Canceling additional moves %s",
                              ops_moves.ids)
                ops_moves.with_context(
                    no_recompute_pack=True, force_cancel=True).action_cancel()
                # A standard picker cannot delete a stock.move
                ops_moves.sudo().unlink()

        res = super(StockPackOperation, self).unlink()
        return res
