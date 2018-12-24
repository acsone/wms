# -*- coding: utf-8 -*-
# Copyright 2016-2018 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, _
from odoo.addons.queue_job.job import job

import logging
_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def do_prepare_partial(self):
        # This method deletes all pack operations and then recreates them.
        # This could trigger action_cancel on stock move but we do not
        # want other moves to try assignment as we will directly re-reserve
        # them.
        return super(
            StockPicking,
            self.with_context(no_auto_reassign=True)
            ).do_prepare_partial()


class StockMove(models.Model):
    _inherit = 'stock.move'

    def action_done(self):
        """ When product is received, check if moves can be assigned """
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
        self.with_delay(description=_(
            'Reassign trial on reception for products ids %s'
            ) % products.ids)._reassign_trial(products)
        return res

    def action_cancel(self):
        """ When move is canceled, check if other moves can be assigned """
        products = self.mapped('product_id')
        res = super(StockMove, self).action_cancel()
        if not self.env.context.get('no_auto_reassign'):
            self.with_delay(description=_(
                'Reassign trial on cancel for products ids %s'
                ) % products.ids)._reassign_trial(products)
        return res

    def write(self, vals):
        """ When priority is lowered, check if other moves can be assigned """
        res = super(StockMove, self).write(vals)
        if vals.get('priority') == '0':
            products = self.mapped('product_id')
            self.with_delay(description=_(
                'Reassign on priority lowered for products ids %s'
                ) % products.ids)._reassign_trial(products)
        return res

    @job(default_channel='root.action_assign')
    def _reassign_trial(self, products):
        """ Find pickings and relaunch reservation """
        if not products:
            return
        moves_pickings = self.search([
            ('picking_id.picking_type_subcode', '=', 'PICK'),
            ('state', '=', 'confirmed'),
            ('product_id', 'in', products.ids),
            ('picking_id.operator_id', '=', False)])
        if not moves_pickings:
            return
        _logger.debug("Products received are in backorder")
        pickings = moves_pickings.mapped('picking_id')
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
