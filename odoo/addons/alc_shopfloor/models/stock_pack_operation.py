# -*- coding: utf-8 -*-
# Copyright 2020 Camptocamp SA (http://www.camptocamp.com)
# Copyright 2021 ACSONE SA/NV (https://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import _, api, exceptions, fields, models
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare

from odoo.addons.procurement.models import procurement


class StockPackOperation(models.Model):
    _name = "stock.pack.operation"
    _inherit = ["stock.pack.operation", "shopfloor.priority.postpone.mixin"]

    # TODO use a serialized field
    shopfloor_unloaded = fields.Boolean(default=False)
    shopfloor_checkout_done = fields.Boolean(default=False)
    shopfloor_user_id = fields.Many2one(comodel_name="res.users", index=True)

    # we search lines based on their location in some workflows
    location_id = fields.Many2one(index=True)
    package_id = fields.Many2one(index=True)

    # allow domain on picking_id.xxx without too much perf penalty
    picking_id = fields.Many2one(auto_join=True)

    priority = fields.Selection(
        selection=procurement.PROCUREMENT_PRIORITIES, compute="_compute_priority"
    )

    product_ids = fields.One2many(
        comodel_name="product.product",
        compute="_compute_product_ids",
        help="technical fields used to get the list of all the products involved "
        "into this pack operation (from package or directly from the operation)",
    )
    lot_ids = fields.One2many(
        comodel_name="stock.production.lot",
        compute="_compute_lot_ids",
        help="technical fields used to get the list of all the lots involved "
        "into this pack operation (from package or directly from the operation)",
    )

    @api.depends(
        "product_id", "package_id", "package_id.parent_id", "package_id.quant_ids"
    )
    def _compute_product_ids(self):
        for rec in self:
            rec.product_ids = rec.product_id
            if rec.package_id:
                rec.product_ids = rec.package_id.ancestor_ids.mapped(
                    "quant_ids.product_id"
                )

    @api.depends(
        "pack_lot_ids",
        "pack_lot_ids.lot_id",
        "package_id",
        "package_id.parent_id",
        "package_id.quant_ids",
    )
    def _compute_lot_ids(self):
        for rec in self:
            rec.lot_ids = rec.mapped("pack_lot_ids.lot_id")
            if rec.package_id:
                rec.lot_ids = rec.package_id.ancestor_ids.mapped("quant_ids.lot_id")

    def _compute_priority(self):
        for rec in self:
            moves = rec.linked_move_operation_ids.mapped("move_id")
            picking = rec.picking_id
            moves = moves.filtered(lambda m, p=picking: m.picking_id == p)
            rec.priority = max(moves.mapped("priority"))

    def _split_pickings_from_source_location(self):
        """Ensure that the related pickings will have the same source location.

        Some pickings related could have other unrelated move lines, as such we
        have to split them to contain only the move lines related to the expected
        source location.

        Example:

            Initial data:

                PICK1:
                    - move line with source location LOC1
                    - move line with source location LOC2
                PICK2:
                    - move line with source location LOC2
                    - move line with source location LOC3

            Then we process move lines related to LOC2 with this method, we get:

                PICK1:
                    - move line with source location LOC1
                PICK2:
                    - move line with source location LOC3
                PICK3:
                    - move line with source location LOC2
                    - move line with source location LOC2

        Return the new picking (in case a split has been made), or the current
        related pickings.
        """
        location_src_to_process = self.mapped("location_id")
        if location_src_to_process and len(location_src_to_process) != 1:
            raise UserError(
                _("Move lines processed have to share the same source location.")
            )
        pickings = self.mapped("picking_id")
        pack_operations_to_process_ids = []
        for picking in pickings:
            location_src = picking.mapped("pack_operation_ids.location_id")
            if len(location_src) == 1:
                continue
            # Get the related move lines among the picking and split them
            pack_operations_to_process_ids.extend(
                set(picking.pack_operation_ids.ids) & set(self.ids)
            )
        # Put all move lines related to the source location in a separate picking
        pack_operation_to_process = self.browse(pack_operations_to_process_ids)
        new_move_ids = []
        for pack_operation in pack_operation_to_process:
            new_move = pack_operation.linked_move_operation_ids.move_id.split_other_pack_operations(
                pack_operation, intersection=True
            )
            # new_move.recalculate_move_state()
            new_move_ids.append(new_move.id)
        # If we have new moves, create the backorder picking
        # NOTE: code copy/pasted & adapted from OCA module 'stock_split_picking'
        new_moves = self.env["stock.move"].browse(new_move_ids)
        if new_moves:
            picking = pickings[0]
            new_picking = picking.copy(
                {"name": "/", "pack_operation_ids": [], "backorder_id": picking.id}
            )
            message = _(
                'The backorder <a href="#" '
                'data-oe-model="stock.picking" '
                'data-oe-id="%d">%s</a> has been created.'
            ) % (new_picking.id, new_picking.name)
            for pick in pickings:
                pick.message_post(body=message)
            new_moves.write({"picking_id": new_picking.id})
            pack_operations = new_moves.mapped(
                "linked_move_operation_ids.operation_id"
            ).filtered(lambda pop, pick=picking: pop.picking_id == pick)
            pack_operations.write({"picking_id": new_picking.id})
            new_picking.action_confirm()
            new_moves.action_assign(no_prepare=True)
            pickings = new_picking
        return pickings

    def _split_qty_to_be_done(self, qty_done, split_partial=True, **split_default_vals):
        """Check qty to be done for current move line. Split it if needed.

        :param qty_done: qty expected to be done
        :param split_partial: split if qty is less than expected
            otherwise rely on a backorder.
        """
        # store a new line if we have split our line (not enough qty)
        new_line = self.env["stock.pack.operation"]
        rounding = self.product_uom_id.rounding
        compare = float_compare(
            qty_done, self.product_uom_qty, precision_rounding=rounding
        )
        qty_lesser = compare == -1
        qty_greater = compare == 1
        if qty_greater:
            return (new_line, "greater")
        if qty_lesser:
            if not split_partial:
                return (new_line, "lesser")
            # split the move line which will be processed later (maybe the user
            # has to pick some goods from another place because the location
            # contained less items than expected)
            remaining = self.product_uom_qty - qty_done
            vals = {"product_uom_qty": remaining, "qty_done": 0}
            vals.update(split_default_vals)
            new_line = self.copy(vals)
            # if we didn't bypass reservation update, the quant reservation
            # would be reduced as much as the deduced quantity, which is wrong
            # as we only moved the quantity to a new move line
            self.with_context(bypass_reservation_update=True).product_uom_qty = qty_done
            return (new_line, "lesser")
        return (new_line, "full")

    def replace_package(self, new_package):
        """Replace a package on an assigned move line"""
        self.ensure_one()

        # search other move lines which should already pick the scanned package
        other_reserved_lines = self.env["stock.pack.operation"].search(
            [
                ("package_id", "=", new_package.id),
                ("state", "in", ("partially_available", "assigned")),
            ]
        )

        # we can't change already picked lines
        unreservable_lines = other_reserved_lines.filtered(
            lambda line: line.qty_done == 0
        )
        to_assign_moves = unreservable_lines.move_id

        # if we leave the package level, it will try to reserve the same
        # one again
        unreservable_lines.package_level_id.explode_package()
        # unreserve qties of other lines
        unreservable_lines.unlink()

        if new_package.location_id != self.location_id:
            if new_package.quant_ids.reserved_quantity:
                # this is a unexpected condition: if we started picking a package
                # in another location, user should never be able to scan it in
                # another location, block the operation
                raise exceptions.UserError(
                    _(
                        "Package {} has been partially picked in another location"
                    ).format(new_package.display_name)
                )
            # the package has been scanned in the current location so we know its
            # a mistake in the data... fix the quant to move the package here
            new_package.move_package_to_location(self.location_id)

        # several move lines can be moved by the package level, if we change
        # the package for the current one, we destroy the package level because
        # we are no longer moving the entire package
        self.package_level_id.explode_package()

        def is_greater(value, other, rounding):
            return float_compare(value, other, precision_rounding=rounding) == 1

        def is_lesser(value, other, rounding):
            return float_compare(value, other, precision_rounding=rounding) == -1

        quant = fields.first(
            new_package.quant_ids.filtered(
                lambda quant: quant.product_id == self.product_id
                and is_greater(
                    quant.qty, quant.reserved_quantity, quant.product_uom_id.rounding,
                )
            )
        )
        if not quant:
            raise exceptions.UserError(
                _(
                    "Package {} does not contain available product {},"
                    " cannot replace package."
                ).format(new_package.display_name, self.product_id.display_name)
            )

        values = {
            "package_id": new_package.id,
            "lot_id": quant.lot_id.id,
            "owner_id": quant.owner_id.id,
            "result_package_id": False,
        }

        available_quantity = quant.quantity - quant.reserved_quantity
        if is_lesser(
            available_quantity, self.product_qty, quant.product_uom_id.rounding
        ):
            new_uom_qty = self.product_id.uom_id._compute_quantity(
                available_quantity, self.product_uom_id, rounding_method="HALF-UP"
            )
            values["product_uom_qty"] = new_uom_qty

        self.write(values)

        # try reassign the move in case we had a partial qty, also, it will
        # recreate a package level if it applies
        if "product_uom_qty" in values:
            # when we change the quantity of the move, the state
            # will still be "assigned" and be skipped by "_action_assign",
            # recompute the state to be "partially_available"
            self.move_id._recompute_state()

        # if the new package has less quantities, assign will create new move
        # lines
        self.move_id._action_assign()

        # Find other available goods for the lines which were using the
        # package before...
        to_assign_moves._action_assign()

        # computation of the 'state' of the package levels is not
        # triggered, force it
        to_assign_moves.move_line_ids.package_level_id.modified(["move_line_ids"])
        self.package_level_id.modified(["move_line_ids"])

    @api.multi
    def _split_quantities_done_preserve_link(self):
        new_op_ids = []
        for operation in self:
            if (
                float_compare(
                    operation.product_qty,
                    operation.qty_done,
                    precision_rounding=operation.product_uom_id.rounding,
                )
                == 1
            ):
                cpy = operation.copy(
                    default={
                        "qty_done": 0.0,
                        "product_qty": operation.product_qty - operation.qty_done,
                    }
                )
                operation.write({"product_qty": operation.qty_done})
                operation._copy_remaining_pack_lot_ids(cpy)
                for link in operation.linked_move_operation_ids:
                    link.copy(default={"operation_id": cpy.id})
                new_op_ids.append(cpy.id)
            else:
                raise UserError(
                    _(
                        "The quantity to split should be smaller than the quantity To Do.  "
                    )
                )
        return self.browse(new_op_ids)
