# -*- coding: utf-8 -*-
# © 2016-2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import time

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

import logging
_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def _create_backorder(self, backorder_moves=[]):
        """ Take care of grouping by partner.
        Reuse the overriden method action_assign that serch a good picking or
        create a new one.
        Apply this to all non-done lines into an existing for a new backorder
        picking. If the key 'do_only_split' is given in the context, then move
        all lines not in context.get('split', []) instead of all non-done
        lines.  """
        if self._context.get('nogrouppicking'):
            return super(StockPicking, self)._create_backorder(
                backorder_moves=backorder_moves)

        picking_togroup = self.filtered(
            lambda p: p.picking_type_id.groupbypartner)
        picking_notgroup = self - picking_togroup

        for picking in picking_togroup:
            backorder_moves = backorder_moves or picking.move_lines
            if self._context.get('do_only_split'):
                not_done_bo_moves = backorder_moves.filtered(
                    lambda move: move.id not in self._context.get('split', []))
            else:
                not_done_bo_moves = backorder_moves.filtered(
                    lambda move: move.state not in ('done', 'cancel'))
            if not not_done_bo_moves:
                continue
            if not picking.printed:
                picking.printed = True
            not_done_bo_moves.with_context(
                backorder_assign=picking).assign_picking()

            if not picking.date_done:
                picking.write({'date_done': time.strftime(
                    DEFAULT_SERVER_DATETIME_FORMAT)})

        if picking_notgroup:
            return super(StockPicking, picking_notgroup)._create_backorder(
                backorder_moves=backorder_moves)

        return self.env['stock.picking']


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    groupbypartner = fields.Boolean(
        'Use existing picking having same partner')
    groupbypartner_maxweight = fields.Integer('Max Weight')


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.multi
    def assign_picking(self):
        """Try to assign the moves to an existing picking
        that has not been reserved yet and that does not have the same
        procurement group but the same partner, locations and picking type
        (moves should already have them identical). Otherwise, create a new
        picking to Assign them to.
        """
        if self._context.get('nogrouppicking'):
            return super(StockMove, self).assign_picking()

        moves_to_group = self.filtered(
            lambda x: x.picking_type_id.groupbypartner)
        moves_to_not_group = self - moves_to_group
        if moves_to_not_group:
            super(StockMove, moves_to_not_group).assign_picking()

        pick_obj = self.env["stock.picking"]
        pickings_cache = {}
        for move in moves_to_group:
            domain = [
                ('partner_id', '=', move.group_id.partner_id.id),
                ('location_id', '=', move.location_id.id),
                ('location_dest_id', '=', move.location_dest_id.id),
                ('picking_type_id', '=', move.picking_type_id.id),
                ('printed', '=', False),
                ('state', 'in', ['draft', 'confirmed', 'waiting',
                                 'partially_available', 'assigned'])
            ]
            if str(domain) in pickings_cache:
                pickings = pickings_cache[str(domain)]
            else:
                pickings = pick_obj.search(domain, order="weight")
                pickings_cache[str(domain)] = pickings

            max_weight = (move.picking_type_id.groupbypartner_maxweight -
                          move.product_id.weight * move.product_qty)
            backorder_orig_id = self.env.context.get('backorder_assign')
            for picking in pickings:
                if (not move.picking_type_id.groupbypartner_maxweight or
                        picking.weight <= max_weight):
                    # assign move to picking
                    _logger.debug("Assign move %s to existing picking %s",
                                  move.id, picking.id)
                    move.picking_id = picking.id
                    if backorder_orig_id:
                        backorder_orig_id.message_post(body=_(
                            "Remaining move moved to exiting picking "
                            "<em>%s</em> used as a backorder.") %
                            (picking.name))
                    # unreserve moves having an operation for that product
                    # Note: (re)check availability (action_assign) does not
                    # work on added move where an operation already exists for
                    # that product. To not recompute all the quants of the
                    # picking, we delete only the pack operation to recompute.
                    # No need to perform the assignment now (new pack operation
                    # creation), it is performed later when the procurement is
                    # run.
                    operations_to_recompute = picking.pack_operation_ids. \
                        filtered(lambda op: op.product_id == move.product_id)
                    if operations_to_recompute:
                        _logger.debug("Cleaning operations %s",
                                      operations_to_recompute.ids)
                        op_linked_moves = operations_to_recompute.mapped(
                            'linked_move_operation_ids.move_id')
                        operations_to_recompute.unlink()
                        op_linked_moves.do_unreserve()
                    break
            else:
                # create a new picking
                _logger.debug("Assign move %s to new picking", move.id)
                values = move._get_new_picking_values()
                picking = pick_obj.create(values)
                if backorder_orig_id:
                    backorder_orig_id.message_post(body=_(
                        "Remaining move moved to new backorder "
                        "<em>%s</em>.") % (picking.name))
                if str(domain) not in pickings_cache:
                    pickings_cache[str(domain)] = picking
                else:
                    pickings_cache[str(domain)] |= picking
                move.picking_id = picking.id
                # see standard assign_picking for why recompute is called
                move.recompute()
        return True

    @api.multi
    def action_cancel(self):
        """ Prevent to cancel a move from a printed picking and recompute pack
        operations """
        _logger.debug("Canceling moves %s", self.ids)
        res = super(StockMove, self).action_cancel()
        if (self.filtered("picking_id.printed") and
                not self.env.context.get('force_cancel')):
            raise UserError(_(
                "You cannot cancel a move that is part of a started picking"))
        if not self.env.context.get('no_recompute_pack'):
            pickings = self.mapped('picking_id').filtered(
                lambda picking: picking.state != 'cancel')
            products = self.mapped('product_id')
            moves = pickings.mapped('move_lines').filtered(
                lambda move: move.state == 'confirmed' and
                move.product_id in products)
            if moves:
                # action_assign requires to clean existing pack operation
                moves.mapped('linked_move_operation_ids.operation_id').unlink()
                _logger.debug("Re-check availability for moves %s", moves.ids)
                moves.action_assign(no_prepare=True)
            # recompute pack op
            _logger.debug("Recompute pack operations")
            pickings.do_prepare_partial()
            # Recompute the weight for each picking
            self.mapped('picking_id')._cal_weight()
        return res
