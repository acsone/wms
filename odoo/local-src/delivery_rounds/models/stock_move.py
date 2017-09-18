# -*- coding: utf-8 -*-
# © 2016-2017 Jacques-Etienne Baudoux (BCIM)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models, _
from odoo.exceptions import ValidationError

import logging
_logger = logging.getLogger(__name__)


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.multi
    def action_assign(self, no_prepare=False):
        """ Picking's moves must be assigned to a delivery round to be reserved
        """
        if not self.env.context.get('round_autoset', True):
            return super(StockMove, self).action_assign(
                no_prepare=no_prepare)

        pick_moves = self.filtered(
            lambda m: m.picking_id.picking_type_subcode == 'PICK')
        has_assigned = False
        for picking in pick_moves.mapped('picking_id'):
            delivery_round = picking.delivery_round_id
            if not delivery_round:
                _logger.debug(
                    "Searching a delivery round for picking %s to assign",
                    picking.id)
                delivery_round = self.env['round.instance'].find(
                    picking.partner_id)
            if delivery_round:
                delivery_round._assign_pickings(picking)
                has_assigned = True
        other_moves = self - pick_moves
        if other_moves:
            super(StockMove, other_moves).action_assign(
                no_prepare=no_prepare)
            has_assigned = True
        if pick_moves and not has_assigned:
            pass
            # Thread not happy with this warning:
            # raise UserError(_("No delivery round instance found"))

    @api.multi
    def action_cancel(self):
        res = super(StockMove, self).action_cancel()
        delivery_round_partner = {}
        for picking in self.mapped('picking_id'):
            if (not picking.partner_id or
                    not picking.delivery_round_id or
                    picking.state != 'cancel'):
                continue
            delivery_round_partner.setdefault(
                picking.delivery_round_id, set()).\
                add(picking.partner_id)
        for delivery_round, partners in delivery_round_partner.iteritems():
            for partner in partners:
                delivery_round._remove_customer(partner)
    @api.multi
    def action_done(self):
        """ Trigger re-reserve on pickings """
        res = super(StockMove, self).action_done()
        received = self.filtered(lambda m: (
            m.location_id.usage not in ('view', 'internal') and
            m.location_dest_id.usage in ('view', 'internal')))
        if not received:
            return res
        products = received.mapped('product_id')
        # Find pickings and relaunch reservation
        output = self.env.ref('stock.stock_location_output')
        moves_pickings = self.search([
            ('location_dest_id', '=', output.id),
            ('state', '=', 'confirmed'),
            ('product_id', 'in', products.ids),
            ('picking_id.printed', '!=', True)])
        pickings = moves_pickings.mapped('picking_id')
        _logger.debug("Products received are in backorder")
        # unreserve moves having an operation for that product
        # Note: (re)check availability (action_assign) does not
        # work on added move where an operation already exists for
        # that product. To not recompute all the quants of the
        # picking, we delete only the pack operation to recompute.
        # No need to perform the assignment now (new pack operation
        # creation), it is performed later when the procurement is
        # run.
        operations_to_recompute = pickings.pack_operation_ids. \
            filtered(lambda op: op.product_id in products)
        if operations_to_recompute:
            _logger.debug("Cleaning operations %s" %
                          operations_to_recompute.ids)
            operations_to_recompute.mapped(
                'linked_move_operation_ids.move_id').do_unreserve()
        _logger.debug("Reserve corresponding moves %s" % moves_pickings)
        moves_pickings.action_assign()
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
                'picking_id.delivery_round_id')
            if len(orig_drs) > 1:
                raise ValidationError(_(
                    "All pickings at destination of a same shipping must "
                    "be in the same delivery round"))
