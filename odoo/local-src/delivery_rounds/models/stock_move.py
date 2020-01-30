# -*- coding: utf-8 -*-
# © 2016-2017 Jacques-Etienne Baudoux (BCIM)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import _, api, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.multi
    def write(self, values):
        picking_id = values.get('picking_id')
        if picking_id:
            # We are assigning the move to a picking ->
            # take a lock on the round instance of the picking (this is a noop
            # if the picking has no round instance) to prevent concurrent
            # access and retries
            picking = self.env['stock.picking'].browse(picking_id)
            if picking.delivery_round_id:
                _logger.info(
                    'setting a new picking %s on move %s (related round: %d)',
                    picking.name,
                    self.ids,
                    picking.delivery_round_id.id,
                )
                picking.delivery_round_id._lock()
        return super(StockMove, self).write(values)

    @api.multi
    def _action_assign_filter_moves(self):
        move_ids = set()
        for move in self:
            picking = move.picking_id
            if picking.picking_type_subcode != 'PICK' or (
                picking.printed and picking.pack_operation_product_ids
            ):
                continue
            move_ids.add(move.id)

        return self.env['stock.move'].browse(move_ids)

    @api.multi
    def action_assign(self, no_prepare=False):
        """ Picking's moves must be assigned to a delivery round to be reserved
        """
        if not self.env.context.get('round_autoset', True):
            return super(StockMove, self).action_assign(no_prepare=no_prepare)

        pick_moves = self._action_assign_filter_moves()

        for picking in pick_moves.mapped('picking_id'):
            if self.env.context.get('round_backorder'):
                # Do not assign a backorder
                continue
            delivery_round = picking.delivery_round_id
            if delivery_round:
                # related picking is already in a delivery round
                pick_moves -= picking.move_lines
                continue
            _logger.debug(
                "Move reservation (action_assign) is searching a "
                "round instance for picking %s",
                picking.id,
            )

            shippings = picking._get_all_dest_pickings().filtered(
                lambda r: r.picking_type_code == 'outgoing'
                and r.state not in ('cancel', 'done')
            )
            if shippings.mapped('carrier_id.delivery_template_id'):
                delivery_round = self.env['round.instance'].find_bytemplate(
                    shippings.mapped('carrier_id.delivery_template_id')[0]
                )
            else:
                delivery_round = self.env['round.instance'].find_bypartner(
                    picking.partner_id
                )
            if delivery_round:
                if picking.partner_id.is_shipping_date_allowed(
                    delivery_round.date
                ):
                    delivery_round._assign_pickings(picking)
        other_moves = self - pick_moves
        if other_moves:
            super(StockMove, other_moves).action_assign(no_prepare=no_prepare)

    @api.multi
    def action_cancel(self):
        res = super(StockMove, self).action_cancel()
        self.mapped('picking_id.delivery_round_customer_id')._remove_if_empty()
        return res

    @api.multi
    @api.constrains('picking_id')
    def _check_round(self):
        if not self.mapped('picking_id.delivery_round_id'):
            return
        for move in self:
            # when a picking is assigned to a move, we have to ensure the whole
            # group (all dest moves) has the same delivery round
            orig_drs = move.mapped('move_orig_ids').mapped(
                'picking_id.delivery_round_id'
            )
            if len(orig_drs) > 1:
                raise ValidationError(
                    _(
                        "All pickings at destination of a same shipping must "
                        "be in the same delivery round"
                    )
                )

    @api.multi
    def _assign_picking_group_domain(self):
        domain = super(StockMove, self)._assign_picking_group_domain()
        orig_picking = self.move_orig_ids.mapped('picking_id')

        if orig_picking and not orig_picking.mapped('delivery_round_id'):
            domain += [
                '|',
                ('delivery_round_id', '=', False),
                ('delivery_round_id.state', 'in', ('open', 'draft')),
            ]
        elif orig_picking and orig_picking.mapped('delivery_round_id'):
            domain += [
                (
                    'delivery_round_customer_id',
                    'in',
                    orig_picking.mapped('delivery_round_customer_id').ids,
                )
            ]
        elif not orig_picking and self._context.get('backorder_assign'):
            back_order_id = self._context['backorder_assign']
            back_order = self.env['stock.picking'].browse(back_order_id)
            domain += [
                (
                    'delivery_round_customer_id',
                    '=',
                    back_order.delivery_round_customer_id.id,
                )
            ]
        else:
            domain += [
                '|',
                ('delivery_round_id', '=', False),
                ('delivery_round_id.state', 'in', ('open', 'draft')),
            ]
        return domain

    @api.multi
    def assign_picking(self):
        res = super(StockMove, self).assign_picking()
        bo_assign = self._context.get('backorder_assign', False)
        if bo_assign:
            bo_assign = self.env['stock.picking'].browse(bo_assign)
        else:
            bo_assign = self.env['stock.picking']
        # if we are assigning the move to a picking in the context of the
        # creation of a backorder, then make sure that 1. the backorder picking
        # lands in the same delivery round as the original picking, and 2. run
        # a job to check the availability of the picking's moves so that if a
        # replenishment has occured, the moves are available. (See ALCYN-2130)
        if bo_assign.delivery_round_id:
            bo_assign.delivery_round_id._assign_pickings(
                self.mapped('picking_id')
            )
            self.mapped('picking_id')._job_action_assign()
        return res
