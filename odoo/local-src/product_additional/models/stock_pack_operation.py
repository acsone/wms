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

        additional_moves = self.mapped('additional_move_id')
        op = additional_moves.mapped('linked_move_operation_ids.operation_id')
        if op.qty_done:
            # A quantity has been already set on the pack op. Keep it.
            # Another one will come back if the main move is reassigned
            # but we don't want to loose what was done.
            return super(StockPackOperation, self).unlink()
        res = super(StockPackOperation, self | op).unlink()
        if additional_moves:
            _logger.debug("Canceling additional moves %s",
                          additional_moves.ids)
            additional_moves.with_context(
                no_recompute_pack=True, force_cancel=True).action_cancel()
            # An standard picker cannot delete a stock.move
            additional_moves.sudo().unlink()
        return res
