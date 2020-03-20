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

        # For PICK backorder, reassign immediately
        if self.env.context.get('round_backorder'):
            return super(
                StockMove,
                self.filtered(
                    lambda m: m.picking_id.delivery_round_customer_id
                    and not m.picking_id.delivery_round_customer_id.delivered
                ),
            ).action_assign(no_prepare=no_prepare)

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

        # Ensure PICK moves are assigned in the same delivery round as the SHIP
        delivery_round_customer = (
            self.move_dest_id.picking_id.delivery_round_customer_id
        )
        if delivery_round_customer:
            domain += [
                ('delivery_round_customer_id', '=', delivery_round_customer.id)
            ]
        else:
            # Do not allow to add moves in a picking that is in a delivery round
            # that is not Open (draft)
            domain += [
                '|',
                ('delivery_round_customer_id', '=', False),
                ('delivery_round_id.state', '=', 'draft'),
            ]
        return domain

    @api.multi
    def _get_new_picking_values(self):
        res = super(StockMove, self)._get_new_picking_values()
        # In case of PICK backorder, keep in the delivery round
        # In case of delivery, move out of delivery round
        if (
            self.picking_id.delivery_round_customer_id
            and not self.picking_id.delivery_round_customer_id.delivered
            and self.picking_id.delivery_round_id.state
            not in ('delivering', 'done')
        ):
            res[
                'delivery_round_customer_id'
            ] = self.picking_id.delivery_round_customer_id.id
            res['rank'] = self.picking_id.rank
        return res
