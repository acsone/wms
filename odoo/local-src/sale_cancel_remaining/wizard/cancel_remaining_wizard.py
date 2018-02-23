# -*- coding: utf-8 -*-
# Copyright 2018 Okia SPRL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, _
from odoo.exceptions import UserError


class CancelRemainingWizard(models.TransientModel):
    _name = 'cancel.remaining.wizard'

    @api.multi
    def cancel_remaining_qty(self):
        active_id = self._context.get('active_id')

        if not active_id:
            raise UserError(_('No sale order line ID found'))
        line = self.env['sale.order.line'].browse(active_id)

        procurements = line.procurement_ids
        moves = procurements.mapped('move_ids')
        moves_qty = sum([move.product_uom_qty for move in moves])

        if line.product_qty_remains_to_deliver != moves_qty:
            raise UserError(
                _('The remaining quantity on the sale order should be the '
                  'same than the quantity on the delivery picking'))

        moves_state = set([move.state for move in moves])
        right_state = {'draft', 'waiting', 'confirmed', 'assigned'}
        if moves_state - right_state:
            raise UserError(_('You cannot cancel a quantity that is part '
                              'of a started picking'))

        internal_pickings = line.order_id.picking_ids.filtered(
            lambda picking: picking.picking_type_code == 'internal')

        internal_stock_move = self.env['stock.move'].search([
            ('picking_id', 'in', internal_pickings.ids),
            ('product_id', '=', line.product_id.id),
            ('state', 'in', ['draft', 'waiting', 'confirmed', 'assigned']),
            ('picking_id.printed', '=', False)
        ])

        if not internal_stock_move:
            raise UserError(_('You cannot cancel a quantity that is part '
                              'of a started picking'))

        procurements.cancel()
        line.write({
            'product_qty_canceled': line.product_qty_remains_to_deliver
        })
