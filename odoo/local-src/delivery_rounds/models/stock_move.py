# -*- coding: utf-8 -*-
# © 2016-2017 Jacques-Etienne Baudoux (BCIM)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models, _
from odoo.exceptions import ValidationError
from odoo.addons.queue_job.job import identity_exact

import logging
_logger = logging.getLogger(__name__)


EXPORT_DESC = 'Export sale order {} to ESB webservice (bo changed)'


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
                picking.id)
            delivery_round = self.env['round.instance'].find(
                picking.partner_id)
            if delivery_round:
                delivery_round._assign_pickings(picking)
        other_moves = self - pick_moves
        if other_moves:
            super(StockMove, other_moves).action_assign(
                no_prepare=no_prepare)

    @api.multi
    def action_cancel(self):
        res = super(StockMove, self).action_cancel()
        self.mapped('picking_id.delivery_round_customer_id')._remove()
        return res

    @api.multi
    def action_done(self):
        """ Trigger re-reserve on pickings """
        if not self:
            return True
        res = super(StockMove, self).action_done()
        stock = self.env.ref('stock.stock_location_stock')
        received = self.filtered(lambda m: (
            m.location_dest_id.parent_left >= stock.parent_left and
            m.location_dest_id.parent_right <= stock.parent_right and
            not (m.location_id.parent_left >= stock.parent_left and
                 m.location_id.parent_right <= stock.parent_right)))
        if not received:
            return res
        products = received.mapped('product_id')
        # Find pickings and relaunch reservation
        moves_pickings = self.search([
            ('picking_id.picking_type_subcode', '=', 'PICK'),
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
        operations_to_recompute = pickings.mapped('pack_operation_ids'). \
            filtered(lambda op: op.product_id in products)
        if operations_to_recompute:
            _logger.debug("Cleaning operations %s",
                          operations_to_recompute.ids)
            operations_to_recompute.mapped(
                'linked_move_operation_ids.move_id').do_unreserve()
        _logger.debug("Reserve corresponding moves %s", moves_pickings)
        moves_pickings.action_assign()

        # Sale order that need to be resend to the esb !
        # Because their back order may have changed
        # Testing for order_id existance has it failed on some Travis tests
        if 'order_id' not in moves_pickings.fields_get_keys():
            return res
        updated_sale_order = moves_pickings.mapped('order_id')
        for so in updated_sale_order:
            if not so.esb_is_exportable():
                continue
            so.with_delay(
                description=EXPORT_DESC.format(so.name),
                identity_key=identity_exact,
            ).esb_export_record()

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
