# -*- coding: utf-8 -*-
# Copyright 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    # Use a boolean instead of reverse relation of
    # 'stock.pack.operation' 'additional_move_id' because some pack operations
    # are deleted when the picking is transfered through do_new_transfer() and
    # this prevent to find the additional moves to not forward to backorder
    is_additional_move = fields.Boolean('Is Additional Move')

    def do_unreserve(self):
        # picking do_unreserve first unlink pack operations and then calls
        # do_unreserve on moves. As we also unlink additional moves, we need to
        # rebuild the record set otherwise it will complain for missing records
        # in the recordset
        if self.ids:
            self = self.search([('id', 'in', self.ids)])
        return super(StockMove, self).do_unreserve()

    def check_move_lots(self):
        # Called in mrp module just after action_assign
        # As recordset changed, we need to rebuild it otherwise it
        # will complain for missing records in the recordset
        if self.ids:
            self = self.search([('id', 'in', self.ids)])
        return super(StockMove, self).check_move_lots()

    def assign_picking(self):
        # Prevent any backorder of additional moves
        other_moves = self.browse()
        for move in self:
            # We are creating a backorder
            if move.picking_id and move.is_additional_move:
                move.with_context(
                    no_recompute_pack=True, force_cancel=True
                ).action_cancel()
                move.picking_id.message_post(
                    body=_(
                        "Remaining additional move '%s' canceled" % move.name
                    )
                )
            else:
                other_moves |= move
        if other_moves:
            return super(StockMove, other_moves).assign_picking()
        return True

    def split(self, qty, restrict_lot_id=False, restrict_partner_id=False):
        # Prevent any partial backorder of additional moves
        new_move_id = super(StockMove, self).split(
            qty,
            restrict_lot_id=restrict_lot_id,
            restrict_partner_id=restrict_partner_id,
        )
        if self.is_additional_move and new_move_id:
            new_move = self.browse(new_move_id)
            new_move.with_context(
                no_recompute_pack=True, force_cancel=True
            ).action_cancel()
            return False
        return new_move_id

    @api.multi
    def _get_moves_to_auto_reassign(self):
        """Overload the method from 'stock_reassign_auto' module to not
        process products related to additional moves.
        """
        moves = super(StockMove, self)._get_moves_to_auto_reassign()
        return moves.filtered(lambda m: not m.is_additional_move)
