# -*- coding: utf-8 -*-
# Copyright 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# Copyright 2018 Okia SPRL <sylvain@okia.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, _
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)


class StockPackOperationLot(models.Model):
    _inherit = 'stock.pack.operation.lot'

    def _skip_lot(self):
        """
        Unreserve the current lot operation and recreate a new lot operation
        with a different lot. This method can be use if an operator
        want to change the reserved lot (out of stock; scrap; ...)
        """
        self.ensure_one()
        op = self.operation_id
        moves = op.linked_move_operation_ids.mapped(
            'move_id')

        # Unreserve all operations on that lot
        moves.do_unreserve()

        # Get the available qty of that lot at that location
        # Consider only unreserved quants
        quants = self.env['stock.quant'].search([
            ('product_id', '=', op.product_id.id),
            ('lot_id', '=', self.lot_id.id),
            ('location_id', '=', op.location_id.id),
            ('qty', '>', 0),
            ('reservation_id', '=', False)])
        if quants:
            # Block the quants that are available.
            # If the operation does not match a reserved move, no quant will be
            # returned.
            self.env.cr.execute(
                "SELECT id FROM stock_quant WHERE id in %s FOR UPDATE NOWAIT",
                (tuple(quants.ids), )
                )
            qty_available = sum([q.qty for q in quants])
            qty_done = self.qty
            qty_to_block = qty_available - qty_done
            if qty_to_block <= 0:
                raise UserError(_('No qty to block.'))

            # Create a move to block this qty
            # Send to a temporary location part of the non-pickable stock
            # This will avoid that this lot will be use later.
            dest_location = self.env.ref('stock_lot_loss.stock_location_14019')

            block_picking = self.env['stock.picking'].create({
                'picking_type_id': self.env.ref(
                    'stock_lot_loss.stock_picking_type_23').id,
                'location_id': op.location_id.id,
                'location_dest_id': dest_location.id,
                'move_lines': [(0, 0, {
                    'name': 'Skip Lot',
                    'product_id': op.product_id.id,
                    'product_uom_qty': qty_to_block,
                    'picking_type_id': self.env.ref(
                        'stock_lot_loss.stock_picking_type_23').id,
                    'location_id': op.location_id.id,
                    'location_dest_id': dest_location.id,
                    'restrict_lot_id': self.lot_id.id,
                    'product_uom': op.product_id.uom_id.id,
                    'origin': 'Operator: %s' % self.env.user.name
                    })]
            })
            block_picking.action_confirm()
            block_picking.action_assign()

        # Recompute pack operations
        moves._recompute_pack_op()
