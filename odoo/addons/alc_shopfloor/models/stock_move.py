# -*- coding: utf-8 -*-
# Copyright 2020 Camptocamp SA (http://www.camptocamp.com)
# Copyright 2021 ACSONE SA/NV (https://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import _, api, fields, models
from odoo.tools.float_utils import float_compare, float_is_zero


class StockMove(models.Model):
    _inherit = "stock.move"

    pack_operation_ids = fields.One2many(
        comodel_name="stock.pack.operation",
        compute="_compute_pack_operation_ids",
        help="Pack operations linked to the move",
    )

    @api.depends("linked_move_operation_ids", "linked_move_operation_ids.move_id")
    def _compute_pack_operation_ids(self):
        for rec in self:
            rec.pack_operation_ids = rec.linked_move_operation_ids.mapped(
                "operation_id"
            )

    def _qty_is_satisfied(self):
        compare = float_compare(
            self.quantity_done,
            self.product_uom_qty,
            precision_rounding=self.product_uom.rounding,
        )
        # greater or equal
        return compare in (0, 1)

    def split_other_pack_operations(self, pack_operations, intersection=False):
        """Substract `pack_operations` from `move.pack_operation_ids`, put the result
        in a new move and returns it.

        If `intersection` is set to `True`, this is the common lines between
        `pack_operations` and `move.pack_operation_ids` which will be put in a new move.
        """
        self.ensure_one()
        if intersection:
            other_pack_operations = self.pack_operation_ids & pack_operations
        else:
            other_pack_operations = self.pack_operation_ids - pack_operations
        if other_pack_operations or self.partially_available:
            qty_by_operation = {
                l.operation_id: l.qty for l in self.linked_move_operation_ids
            }
            if intersection:
                # TODO @sebalix: please check if we can abandon the flag.
                qty_to_split = sum([qty_by_operation[o] for o in other_pack_operations])
            else:
                qty_to_split = self.product_uom_qty - sum(
                    [qty_by_operation[o] for o in pack_operations]
                )
            backorder_move_id = self.split(qty_to_split)
            backorder_move = self.browse(backorder_move_id)
            other_pack_operations.linked_move_operation_ids.filtered(
                lambda lk, mv=self: lk.move_id == mv
            ).write({"move_id": backorder_move.id})
            # we must also split quants and reassing to the backorder move
            rounding = self.product_id.uom_id.rounding
            quants_to_reserve = self.env["stock.quant"]
            reserved_qty = sum(self.reserved_quant_ids.mapped("qty"))
            reserved_qty_to_split = reserved_qty - qty_to_split
            if float_compare(reserved_qty_to_split, 0, precision_rounding=rounding) > 0:
                for quant in self.reserved_quant_ids:
                    if (
                        quant.package_id
                        and quant.package_id == pack_operations.package_id
                    ):
                        # don't split package linked to pack_operations.
                        continue
                    if (
                        float_compare(
                            quant.qty, qty_to_split, precision_rounding=rounding
                        )
                        <= 0
                    ):
                        quants_to_reserve |= quant
                        qty_to_split -= quant.qty
                    else:
                        new_quant = quant._quant_split(quant.qty - qty_to_split)
                        quants_to_reserve |= new_quant
                        break
                    if float_is_zero(qty_to_split, precision_rounding=rounding):
                        break
            self.env["stock.quant"].quants_reserve(
                [(q, q.qty) for q in quants_to_reserve], backorder_move
            )
            self._recompute_state()
            backorder_move._recompute_state()
            return backorder_move
        return self.browse()

    def split_unavailable_qty(self):
        """Put unavailable qty of a partially available move in their own
        move (which will be 'confirmed').
        """
        partial_moves = self.filtered(
            lambda m: m.state == "confirmed" and m.partially_available
        )
        for partial_move in partial_moves:
            partial_move.split_other_pack_operations(partial_move.pack_operation_ids)
        return partial_moves

    def extract_and_action_done(self):
        """Extract the moves in a separate transfer and validate them.

        You can combine this method with `split_other_pack_operations` method
        to first extract some move lines in a separate move, then validate it
        with this method.
        """
        # Process assigned moves
        moves = self.filtered(lambda m: m.state == "assigned")
        if not moves:
            return False
        for picking in moves.mapped("picking_id"):
            moves_todo = picking.move_lines & moves
            # No need to create a new transfer if we are processing all moves
            if moves_todo == picking.move_lines:
                new_picking = picking
            # We process some available moves of the picking, but there are still
            # some other moves to process, then we put the moves to process in
            # a new transfer to validate. All remaining moves stay in the
            # current transfer.
            else:
                new_picking = picking.copy(
                    {
                        "name": "/",
                        "move_lines": [],
                        "pack_operation_ids": [],
                        "backorder_id": picking.id,
                    }
                )
                new_picking.message_post(
                    body=_(
                        "Created from backorder "
                        "<a href=# data-oe-model=stock.picking data-oe-id=%d>%s</a>."
                    )
                    % (picking.id, picking.name)
                )
                moves_todo.write({"picking_id": new_picking.id})
                pack_operations = moves_todo.mapped(
                    "linked_move_operation_ids.operation_id"
                ).filtered(lambda pop, pick=picking: pop.picking_id == pick)
                pack_operations.write({"picking_id": new_picking.id})

                # NOTE: at this stage all the operations should be assigned already
                # hence the new picking must be assigned already.
                # DO NOT CALL `new_picking.action_assign` or you'll wipe qty_done.
                assert new_picking.state == "assigned"
            new_picking.action_done()
        return True

    def _recompute_state(self):
        # do not use recalculate_move_state since we must also take into
        # account the reserved_availabitlity and we MUST avoid the
        # shit into the override done in stock_reassign_auto
        for move in self:
            if move.reserved_availability == move.product_uom_qty:
                move.state = "assigned"
            else:
                vals = {}
                reserved_quant_ids = move.reserved_quant_ids
                if len(reserved_quant_ids) > 0 and not move.partially_available:
                    vals["partially_available"] = True
                if len(reserved_quant_ids) == 0 and move.partially_available:
                    vals["partially_available"] = False
                if move.state == "assigned":
                    if (
                        move.procure_method == "make_to_order"
                        or move.find_move_ancestors()
                    ):
                        vals["state"] = "waiting"
                    else:
                        vals["state"] = "confirmed"
                if vals:
                    move.write(vals)
