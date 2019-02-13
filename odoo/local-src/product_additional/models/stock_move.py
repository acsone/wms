# -*- coding: utf-8 -*-
# Copyright 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, _


class StockMove(models.Model):
    _inherit = 'stock.move'

    additional_move_src_ids = fields.One2many(
        'stock.pack.operation', 'additional_move_id',
        'Additional Move Source')

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
        if self.env.context.get('backorder_assign'):
            additional_moves = self.filtered('additional_move_src_ids')
            if additional_moves:
                additional_moves.with_context(
                    no_recompute_pack=True, force_cancel=True).action_cancel()
                for move in additional_moves:
                    if not move.picking_id:
                        continue
                    move.picking_id.message_post(body=_(
                        "Remaining additional move '%s' canceled" % move.name))
            other_moves = self - additional_moves
            if other_moves:
                return super(StockMove, other_moves).assign_picking()
            return True
        return super(StockMove, self).assign_picking()
