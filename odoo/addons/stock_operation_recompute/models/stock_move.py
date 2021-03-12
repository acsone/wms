# -*- coding: utf-8 -*-
# Copyright 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import _, models
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare

_logger = logging.getLogger(__name__)


class StockMove(models.Model):
    _inherit = "stock.move"

    def _recompute_pack_op(self):  # noqa: C901
        picking = self.mapped("picking_id")
        picking.ensure_one()

        # Re-reserve quants
        self.action_assign(no_prepare=True)

        # Backup qty done
        ops = self.mapped("linked_move_operation_ids.operation_id")
        for op in ops:
            _logger.debug(
                "Old operation %s %s",
                op,
                [
                    u"{}: {}/{}".format(plot.lot_id, plot.qty, plot.qty_todo)
                    for plot in op.pack_lot_ids
                ],
            )
        qty_done = {}
        for op in ops:
            done = qty_done.setdefault(op.location_id.id, {})
            if op.product_id.tracking == "none" and op.qty_done:
                # Set 0 as lot_id for products without tracking
                done[0] = op.qty_done
                continue
            for l in op.pack_lot_ids:
                if l.qty:
                    done[l.lot_id.id] = l.qty

        # Check if product additional has been done
        additional_ctx = {}
        additional_moves = self.mapped("additional_move_ids")
        if any(
            additional_moves.mapped("linked_move_operation_ids.operation_id.qty_done")
        ) or any(self.mapped("is_additional_move")):
            additional_ctx = dict(skip_additional=True)

        # Delete pack op
        ops.with_context(**additional_ctx).unlink()

        # Re-generate pack ops - similar to do_prepare_partial
        forced_qties = {}
        picking_quants = self.env["stock.quant"]
        for move in self:
            if move.state not in ("assigned", "confirmed", "waiting"):
                continue
            move_quants = move.reserved_quant_ids
            picking_quants |= move_quants
            forced_qty = 0.0
            if move.state == "assigned":
                qty = move.product_uom._compute_quantity(
                    move.product_uom_qty, move.product_id.uom_id, round=False
                )
                forced_qty = qty - sum([x.qty for x in move_quants])
            # if we used force_assign() on the move, or if the move is
            # incoming, forced_qty > 0
            if (
                float_compare(
                    forced_qty, 0, precision_rounding=move.product_id.uom_id.rounding
                )
                > 0
            ):
                if forced_qties.get(move.product_id):
                    forced_qties[move.product_id] += forced_qty
                else:
                    forced_qties[move.product_id] = forced_qty
        new_ops = self.env["stock.pack.operation"]
        for vals in picking.with_context(**additional_ctx)._prepare_pack_ops(
            picking_quants, forced_qties
        ):
            new_ops |= new_ops.create(vals)
        # New pack operations could contain additional products.
        # Filter them out
        new_ops = new_ops.filtered(lambda o: o.product_id in self.mapped("product_id"))

        # Recover the qty done
        for location_id, lines in qty_done.iteritems():
            for lot_id, qty in lines.iteritems():
                nop = new_ops.filtered(
                    lambda op, loc_id=location_id: op.location_id.id == loc_id
                )
                # lot_id == 0 on products without tracking
                if not lot_id:
                    nop.qty_done = qty
                else:
                    nol = nop.pack_lot_ids.filtered(
                        lambda line, l_id=lot_id: line.lot_id.id == l_id
                    )
                    if not nol:
                        raise UserError(
                            _(
                                "Internal Error. "
                                "Cannot match done lot in new pack operation"
                            )
                        )
                    nol.qty = qty

        new_ops.save()

        # recompute the remaining quantities all at once
        picking.do_recompute_remaining_quantities()
        for pack in new_ops:
            pack.ordered_qty = sum(
                pack.mapped("linked_move_operation_ids")
                .mapped("move_id")
                .filtered(lambda r: r.state != "cancel")
                .mapped("ordered_qty")
            )

        for new_mop in self.mapped("linked_move_operation_ids.operation_id"):
            _logger.debug(
                "New operation %s %s",
                new_mop,
                [
                    u"{}: {}/{}".format(plot.lot_id, plot.qty, plot.qty_todo)
                    for plot in new_mop.pack_lot_ids
                ],
            )
