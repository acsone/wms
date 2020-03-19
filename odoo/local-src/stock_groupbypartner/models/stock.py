# -*- coding: utf-8 -*-
# © 2016-2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
import time
from itertools import groupby

from odoo import _, api, fields, models
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def _lock(self):
        """Lock the database rows of the picking to prevent concurrent access.

        The lock is released when the transaction is committed or rolled back.

        This method is called:
        1. when adding a move in the picking to prevent the picking to be started
        2. when detaching the picking from delivery round (no_new_picking)
        3. when assigning the picking to a delivery round to prevent new moves to be added
        """
        if self:
            _logger.info('acquire lock for pickings %s', self.ids)
            self.env.cr.execute(
                'SELECT printed FROM stock_picking WHERE id in %s FOR UPDATE',
                (tuple(self.ids),),
            )
            _logger.info('lock acquired for pickings %s', self.ids)
        return

    @api.multi
    def _create_backorder(self, backorder_moves=[]):
        """ Take care of grouping by partner.
        Reuse the overriden method action_assign that search a good picking or
        create a new one.
        Apply this to all non-done lines into an existing for a new backorder
        picking. If the key 'do_only_split' is given in the context, then move
        all lines not in context.get('split', []) instead of all non-done
        lines.
        Pay attention to unsafe standard signature "backorder_moves=[]".
        """
        backorders = self.env['stock.picking']

        picking_togroup = self.filtered(
            lambda p: p.picking_type_id.groupbypartner
        )
        picking_notgroup = self - picking_togroup

        for picking in picking_togroup:
            if self._context.get('do_only_split'):
                not_done_bo_moves = picking.move_lines.filtered(
                    lambda move: move.id not in self._context.get('split', [])
                )
            else:
                not_done_bo_moves = picking.move_lines.filtered(
                    lambda move: move.state not in ('done', 'cancel')
                )
            if not not_done_bo_moves:
                continue
            if not picking.printed:
                # Mark delivery as processed. When reassigning move in
                # backorder, we look for picking not printed
                picking.printed = True

            if self.env.context.get('cancel_backorder'):
                # Triggerred by delivery round shipping delivery
                # for partner that does not accept backorder
                not_done_bo_moves.with_context(
                    no_recompute_pack=True, force_cancel=True
                ).action_cancel()
                picking.message_post(
                    body=_(
                        "Remaining moves canceled as partner does not "
                        "accept backorder:<ul>%s</ul>"
                        % ''.join(
                            [
                                '<li>%s</li>' % m
                                for m in not_done_bo_moves.mapped('name')
                            ]
                        )
                    )
                )

                def key(r):
                    return r.picking_id

                cancel_moves = (
                    not_done_bo_moves.filtered(lambda move: move.propagate)
                    .mapped('move_orig_ids')
                    .filtered(
                        lambda move: move.state not in ('cancel', 'done')
                    )
                    .sorted(key=key)
                )
                # Propagate to picking
                for cancel_picking, cancel_moves_iter in groupby(
                    cancel_moves, key=key
                ):
                    cancel_moves_bypicking = reduce(
                        lambda x, y: x | y, cancel_moves_iter
                    )
                    cancel_moves_bypicking.with_context(
                        no_recompute_pack=True, force_cancel=True
                    ).action_cancel()
                    cancel_picking.message_post(
                        body=_(
                            "Remaining moves canceled as partner does not "
                            "accept backorder:<ul>%s</ul>"
                            % ''.join(
                                [
                                    '<li>%s</li>' % m
                                    for m in cancel_moves_bypicking.mapped(
                                        'name'
                                    )
                                ]
                            )
                        )
                    )

            else:
                not_done_bo_moves.assign_picking()

            if not picking.date_done:
                picking.write(
                    {
                        'date_done': time.strftime(
                            DEFAULT_SERVER_DATETIME_FORMAT
                        )
                    }
                )
            # In the call to assign_picking, additional products have been
            # canceled.
            not_done_bo_moves = not_done_bo_moves.filtered(
                # we need to check if the move exists because we can have
                # deleted moves in case of additional products
                lambda move: move.exists()
                and move.state not in ('done', 'cancel')
            )
            backorders |= not_done_bo_moves.mapped('picking_id')
        if backorders:
            # In standard, created backorders are assigned at the end of the
            # method
            backorders.action_assign()

        for picking in picking_notgroup:
            # Do not call _create_backorder on recordset due to unsafe
            # signature "backorder_moves=[]" and ensure backorder_moves is
            # correctly set
            backorders |= super(StockPicking, picking)._create_backorder(
                backorder_moves=picking.move_lines
            )

        return backorders


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    groupbypartner = fields.Boolean('Use existing picking having same partner')
    groupbypartner_maxweight = fields.Integer('Max Weight')


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.multi
    def _assign_picking_group_domain(self):
        self.ensure_one()
        domain = [
            ('partner_id', '=', self.group_id.partner_id.id),
            ('location_id', '=', self.location_id.id),
            ('location_dest_id', '=', self.location_dest_id.id),
            ('picking_type_id', '=', self.picking_type_id.id),
            ('printed', '=', False),
            ('state', 'not in', ('draft', 'cancel', 'done')),
        ]
        return domain

    @api.multi
    def assign_picking(self):
        """Try to assign the moves to an existing picking
        that has not been reserved yet and that does not have the same
        procurement group but the same partner, locations and picking type
        (moves should already have them identical). Otherwise, create a new
        picking to Assign them to.
        """
        moves_to_group = self.filtered(
            lambda x: x.picking_type_id.groupbypartner
        )

        moves_to_not_group = self - moves_to_group
        if moves_to_not_group:
            super(StockMove, moves_to_not_group).assign_picking()

        pick_obj = self.env["stock.picking"]
        pickings_cache = {}
        if moves_to_group.mapped('picking_id'):
            recompute_sale_pickings = True
        else:
            recompute_sale_pickings = False
        for move in moves_to_group:
            domain = move._assign_picking_group_domain()
            if str(domain) in pickings_cache:
                pickings = pickings_cache[str(domain)]
            else:
                pickings = pick_obj.search(domain, order="weight")
                pickings_cache[str(domain)] = pickings

            max_weight = (
                move.picking_type_id.groupbypartner_maxweight
                - move.product_id.weight * move.product_qty
            )
            backorder_orig_id = move.picking_id

            # Preferably assign the move in a picking having a move with the
            # same group_id. Necessary for pushed moves
            if len(pickings) > 1:

                def key(r):
                    return not (
                        move.group_id
                        and move.group_id
                        in r.move_lines.filtered(
                            lambda m: m.state not in ('cancel', 'done')
                        ).mapped('group_id')
                    )

                pickings = pickings.sorted(key=key)
            # Select the right picking to assign to
            for picking in pickings:
                # Ensure the move related carrier matches the picking related
                # carrier. This is not part of _assign_picking_group_domain for
                # performance reasons
                if picking.group_id.carrier_id != move.group_id.carrier_id:
                    continue
                if (
                    move.picking_id != picking
                    and move.picking_type_id.groupbypartner_maxweight
                    and picking.weight > max_weight
                ):
                    continue
                if move.picking_id != picking:
                    # assign move to picking
                    _logger.debug(
                        "Assign move %s to existing picking %s (%s)",
                        move.id,
                        picking.id,
                        picking.name,
                    )
                    picking._lock()
                    move.picking_id = picking.id
                    if backorder_orig_id:
                        backorder_orig_id.message_post(
                            body=_(
                                "Remaining move '%s' of qty %s and origin '%s' "
                                "moved to exiting picking "
                                "<em>%s</em> used as "
                                "a backorder."
                            )
                            % (
                                move.product_id.display_name,
                                move.product_uom_qty,
                                move.group_id.name,
                                picking.name,
                            )
                        )
                # unreserve moves having an operation for that product
                # Note: (re)check availability (action_assign) does not
                # work on added move where an operation already exists for
                # that product. To not recompute all the quants of the
                # picking, we delete only the pack operation to recompute.
                # No need to perform the assignment now (new pack operation
                # creation), it is performed later when the procurement is
                # run.
                # If the new move is in waiting state (line added in a
                # ship), then do not cleanup the pack operation as it won't
                # be recomputed
                if move.state == 'waiting':
                    break
                operations_to_recompute = picking.pack_operation_ids.filtered(
                    lambda op: op.product_id == move.product_id
                )
                if operations_to_recompute:
                    _logger.debug(
                        "Cleaning operations %s", operations_to_recompute.ids
                    )
                    op_linked_moves = operations_to_recompute.mapped(
                        'linked_move_operation_ids.move_id'
                    )
                    operations_to_recompute.unlink()
                    op_linked_moves.do_unreserve()
                else:
                    move.do_unreserve()
                break

            else:
                if self.env.context.get('no_new_picking') and not any(
                    pm.state == 'done' for pm in move.picking_id.move_lines
                ):
                    # if picking has not been processed, we can use it as backorder
                    move.picking_id._lock()
                    picking = move.picking_id
                else:
                    # create a new picking
                    values = move._get_new_picking_values()
                    picking = pick_obj.create(values)
                    _logger.debug(
                        "Assign move %s to new picking %s (%s)",
                        move.id,
                        picking.id,
                        picking.name,
                    )
                    if backorder_orig_id:
                        picking.message_post(
                            body=_("Backorder of %s" % backorder_orig_id.name)
                        )
                        backorder_orig_id.message_post(
                            body=_(
                                "Remaining move '%s' moved to new backorder "
                                "<em>%s</em>."
                            )
                            % (move.product_id.display_name, picking.name)
                        )
                    move.picking_id = picking.id
                if str(domain) not in pickings_cache:
                    pickings_cache[str(domain)] = picking
                else:
                    pickings_cache[str(domain)] |= picking
                move.do_unreserve()
                # see standard assign_picking for why recompute is called
                move.recompute()
        if recompute_sale_pickings:
            procurement_groups = moves_to_group.mapped('group_id')
            sales = self.env['sale.order'].search(
                [('procurement_group_id', 'in', procurement_groups.ids)]
            )
            # force recompute of picking_ids
            sales.modified(['procurement_group_id'])
        return True

    @api.multi
    def action_cancel(self):
        """ Prevent to cancel a move from a printed picking and recompute pack
        operations """
        _logger.debug("Canceling moves %s", self.ids)
        res = super(StockMove, self).action_cancel()
        if not self.env.context.get('no_recompute_pack'):
            pickings = self.mapped('picking_id').filtered(
                lambda picking: picking.state != 'cancel'
            )
            products = self.mapped('product_id')
            moves = pickings.mapped('move_lines').filtered(
                lambda move: move.state == 'confirmed'
                and move.product_id in products
            )
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
