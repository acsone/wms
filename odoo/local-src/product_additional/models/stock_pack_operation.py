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
        if not self:
            return True
        if self.env.context.get('skip_additional'):
            return super(StockPackOperation, self).unlink()

        moves_to_cancel = self.env['stock.move'].browse()
        for additional_move in self.mapped('additional_move_id'):
            ops = additional_move.mapped(
                'linked_move_operation_ids.operation_id')
            ops_done = ops.filtered('qty_done')
            # If a quantity has been already set on the pack op. Keep it.
            # Another one will come back if the main move is reassigned
            # but we don't want to loose what was done.
            if not ops_done:
                moves_to_cancel |= additional_move
                ops_to_delete = ops - self
                if ops_to_delete:
                    super(StockPackOperation, ops_to_delete).unlink()

        if moves_to_cancel:
            _logger.debug("Canceling additional moves %s",
                          moves_to_cancel.ids)
            moves_to_cancel.with_context(
                no_recompute_pack=True, force_cancel=True).action_cancel()
            # A standard picker cannot delete a stock.move
            #moves_to_cancel.sudo().with_context(
            #    recompute=False,
            #        ).unlink()

        super(StockPackOperation, self).with_context(
            skip_additional=True).unlink()
        return True
