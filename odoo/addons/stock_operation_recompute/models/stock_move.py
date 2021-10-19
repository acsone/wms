# -*- coding: utf-8 -*-
# Copyright 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from collections import defaultdict, namedtuple

from odoo import api, fields, models
from odoo.tools.float_utils import float_compare

_logger = logging.getLogger(__name__)

OperationKey = namedtuple(
    "OperationKey", ["product_id", "location_id", "package_id", "lot_id", "picking_id"]
)


class StockMove(models.Model):
    _inherit = "stock.move"

    is_missing_packop = fields.Boolean(
        default=False, compute="_compute_is_missing_packop"
    )

    @api.depends("linked_move_operation_ids", "linked_move_operation_ids.operation_id")
    def _compute_is_missing_packop(self):
        for move in self:
            move.is_missing_packop = not move.mapped(
                "linked_move_operation_ids.operation_id"
            )

    @api.model
    def _to_operation_key(self, operation, lot=None):
        key = {
            "product_id": operation.product_id.id,
            "location_id": operation.location_id.id,
            "package_id": operation.package_id.id,
            "lot_id": lot.id if lot else None,
            "picking_id": operation.picking_id.id,
        }
        return OperationKey(**key)

    def _backup_operation_to_recompute_info(self):
        ret = {}
        for rec in self:
            for op in rec.mapped("linked_move_operation_ids.operation_id"):
                values = op._backup_for_recompute()[0]
                if op.pack_lot_ids:
                    for pack_lot in op.pack_lot_ids:
                        key = rec._to_operation_key(op, pack_lot.lot_id)
                        ret[key] = values
                else:
                    key = rec._to_operation_key(op)
                    ret[key] = values
        return ret

    @api.model
    def _recover_pack_op_datas(self, operation, operations_data_backup):
        key = self._to_operation_key(operation=operation)
        backup = operations_data_backup.get(key)
        if not backup:
            return
        self._update_operation_from_backup(operation, backup.copy())

    @api.model
    def _recover_pack_op_lot_datas(self, operation, operations_data_backup):
        if not operation.pack_lot_ids:
            return
        operation_updated = False
        for pack_lot in operation.pack_lot_ids:
            lot = pack_lot.lot_id
            key = self._to_operation_key(operation=operation, lot=lot)
            backup = operations_data_backup.get(key)
            if not backup:
                continue
            if not operation_updated:
                self._update_operation_from_backup(operation, backup.copy())
                operation_updated = True
            lot_backup = backup["lots"].get(lot.id)
            if lot_backup:
                self._update_lot_operation_from_backup(pack_lot, lot_backup.copy())

    @api.model
    def _update_operation_from_backup(self, operation, backup):
        backup.pop("lots", None)
        operation.write(backup)

    @api.model
    def _update_lot_operation_from_backup(self, lot_operation, backup):
        lot_operation.write(backup)

    @api.model
    def _recover_pack_ops_datas(self, new_ops, operations_data_backup):
        for operation in new_ops:
            if operation.pack_lot_ids:
                self._recover_pack_op_lot_datas(operation, operations_data_backup)
            else:
                self._recover_pack_op_datas(operation, operations_data_backup)

    def _recompute_pack_op(self):  # noqa: C901
        # Re-reserve quants
        self.action_assign(no_prepare=True)

        # preserve some informations
        operations_data_backup = self._backup_operation_to_recompute_info()

        moves_by_picking = defaultdict(list)
        for m in self:
            moves_by_picking[m.picking_id].append(m.id)
        moves_by_picking = {k: self.browse(v) for k, v in moves_by_picking.items()}

        for picking, moves in moves_by_picking.items():

            # Check if product additional has been done
            additional_ctx = {}
            additional_moves = moves.mapped("additional_move_ids")
            if any(
                additional_moves.mapped(
                    "linked_move_operation_ids.operation_id.qty_done"
                )
            ) or any(moves.mapped("is_additional_move")):
                additional_ctx = dict(skip_additional=True)

            # Delete pack op
            ops = moves.mapped("linked_move_operation_ids.operation_id")
            ops.with_context(**additional_ctx).unlink()

            # Re-generate pack ops - similar to do_prepare_partial
            forced_qties = {}
            picking_quants = moves.env["stock.quant"]
            for move in moves:
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
                        forced_qty,
                        0,
                        precision_rounding=move.product_id.uom_id.rounding,
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
            new_ops = new_ops.filtered(
                lambda o, moves=moves: o.product_id in moves.mapped("product_id")
            )

            # Recover data
            self._recover_pack_ops_datas(new_ops, operations_data_backup)
            # recompute the remaining quantities all at once
            picking.do_recompute_remaining_quantities()
            for pack in new_ops:
                pack.ordered_qty = sum(
                    pack.mapped("linked_move_operation_ids")
                    .mapped("move_id")
                    .filtered(lambda r: r.state != "cancel")
                    .mapped("ordered_qty")
                )

            for new_mop in moves.mapped("linked_move_operation_ids.operation_id"):
                _logger.debug(
                    "New operation %s %s",
                    new_mop,
                    [
                        u"{}: {}/{}".format(plot.lot_id, plot.qty, plot.qty_todo)
                        for plot in new_mop.pack_lot_ids
                    ],
                )

    def do_recompute_pack_operation(self):
        to_recompute = self.filtered(
            lambda m: m.state in ("assigned", "confirmed") and m.is_missing_packop
        )
        to_recompute._recompute_pack_op()
