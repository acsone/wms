# Copyright 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging
from typing import Self

from odoo import _, api, fields
from odoo.tools import float_compare

from odoo.addons.stock_move_propagate_first_move.models.stock_move import (
    StockMove as StockMoveBase,
)

_logger = logging.getLogger(__name__)


class StockMove(StockMoveBase):

    is_additional_move = fields.Boolean(string="Is Additional Move")
    main_move_id = fields.Many2one[StockMoveBase](
        string="Main Product Move",
        ondelete="set null",
        index=True,
        help="Link to the main product for stock moves created for additional products",
    )
    additional_move_ids = fields.One2many[StockMoveBase](
        inverse_name="main_move_id",
        string="Additional Product Moves",
        help="Optional: stock move for additional products linked to the current product",
    )
    additional_product_on_reserved_qty_allowed = fields.Boolean(
        compute="_compute_additional_product_on_reserved_qty_allowed"
    )

    @api.depends(
        "picking_type_id.allow_additional_product_on_reserved_qty",
        "first_picking_type_id.code",
        "picking_type_id.code",
        "move_orig_ids",
    )
    def _compute_additional_product_on_reserved_qty_allowed(self):
        for rec in self:
            rec.additional_product_on_reserved_qty_allowed = (
                rec.product_id.additional_product_id
                and rec.picking_type_id.allow_additional_product_on_reserved_qty
                and rec.first_picking_type_id.code == "outgoing"
                and not rec.move_orig_ids
            )

    def _add_additional_products(self):
        procurements = []
        for move in self:
            if not move.additional_product_on_reserved_qty_allowed:
                continue
            procurement = move._get_additional_product_procurement()
            if procurement:
                procurements.append(procurement)
        self.env["procurement.group"].run(procurements)

    def _get_additional_product_display_name(self, additional_product):
        return _(
            "ADDITIONAL PRODUCT: %(ap_name)s (FROM %(m_p_name)s)",
            ap_name=additional_product.display_name,
            m_p_name=self.product_id.display_name,
        )

    def _get_additional_product_procurement(self):
        self.ensure_one()
        first_move = self.first_move_id
        additional_product = first_move.product_id.additional_product_id
        product_qty = first_move.product_id._get_qty_additional_product(
            self.reserved_availability
        )
        if not product_qty or not additional_product:
            return False
        return self.env["procurement.group"].Procurement(
            additional_product,
            product_qty,
            additional_product.uom_id,
            first_move.location_dest_id,
            first_move._get_additional_product_display_name(additional_product),
            first_move.name,
            first_move.company_id,
            first_move._prepare_additional_product_procurement_values(first_move),
        )

    def _prepare_additional_product_procurement_values(self, first_move):
        self.ensure_one()
        return {
            "group_id": first_move.group_id,
            "date_planned": first_move.date,
            "date_deadline": first_move.date_deadline,
            "route_ids": first_move.route_ids,
            "warehouse_id": first_move.warehouse_id,
            "partner_id": first_move.partner_id.id,
            "company_id": first_move.company_id,
            "sequence": first_move.sequence,
            "main_move_id": first_move.id,
            "picking_id": first_move.picking_id.id,
            "is_additional_move": True,
            "picking_description": first_move._get_additional_product_display_name(
                first_move.product_id.additional_product_id
            ),
        }

    def _action_assign(self, force_qty=False):
        reserved_qty_by_move = {
            move: move.reserved_availability
            for move in self
            if move.state not in ("done", "cancel")
        }
        res = super()._action_assign(force_qty=force_qty)
        updated_moves = self.filtered(
            lambda m: m.reserved_availability != reserved_qty_by_move.get(m)
        )
        main_moves = updated_moves.filtered(lambda m: not m.is_additional_move)
        main_moves._remove_all_additional_moves_on_assign()
        main_moves._add_additional_products()
        additional_moves = main_moves.additional_move_ids
        if additional_moves:
            additional_moves._action_assign(force_qty=force_qty)
        return res

    def _action_cancel(self):
        res = super()._action_cancel()
        additional_moves = self.mapped("additional_move_ids")
        if additional_moves:
            return additional_moves.with_context(force_cancel=True)._action_cancel()
        return res

    def _get_all_not_done_additional_moves(self) -> Self:
        """This will returns all moves that should be cancelled."""
        if not self.is_additional_move:
            first_move = self.first_move_id
            first_additional_move = first_move.additional_move_ids
            return self.search(
                [
                    ("first_move_id", "in", first_additional_move.ids),
                    ("state", "not in", ("done", "cancel")),
                    ("quantity_done", "=", 0),
                ]
            ) | first_additional_move.filtered(
                lambda move: move.state not in ("cancel", "done")
            )
        return self.browse()

    def _remove_all_additional_moves_on_assign(self):
        for move in self:
            if not move.additional_product_on_reserved_qty_allowed:
                continue
            # we can't cancel an additional move at assign if an origin move
            # has been picked
            first_move = self.first_move_id
            first_additional_move = first_move.additional_move_ids
            moves_to_remove = self.browse()
            for additional_move in first_additional_move:
                all_origin_moves = self.browse()
                origin_move = additional_move.move_orig_ids
                while origin_move:
                    all_origin_moves |= origin_move
                    origin_move = origin_move.move_orig_ids
                if any(
                    origin_move.state == "done" or origin_move.quantity_done > 0
                    for origin_move in all_origin_moves
                    if origin_move.state != "cancel"
                ):
                    continue
                moves_to_remove |= additional_move
            if moves_to_remove:
                moves_to_remove.with_context(force_cancel=True)._action_cancel()
                # TODO: Mark moves as 'to delete' instead. This is a workaround as
                # a glue module should be done between this and stock_dynamic_routing
                # (to confirm)
                # moves_to_remove.sudo().unlink()

    @api.model
    def _prepare_merge_moves_distinct_fields(self):
        return super()._prepare_merge_moves_distinct_fields() + [
            "main_move_id",
            "is_additional_move",
        ]

    def _additional_move_split_and_cancel_not_done_qty(self):
        """
        At picking done this method is called to split undone additional moves and.

        cancel the remaining qty. It also cancel all potential backorders for the
        additional move
        """
        precision_digits = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        for move in self:
            if move.state == "cancel" or not move.is_additional_move:
                continue
            quantity_todo = move.product_uom._compute_quantity(
                move.product_uom_qty, move.product_id.uom_id, rounding_method="HALF-UP"
            )
            quantity_done = move.product_uom._compute_quantity(
                move.quantity_done, move.product_id.uom_id, rounding_method="HALF-UP"
            )
            if (
                float_compare(
                    quantity_done,
                    quantity_todo,
                    precision_digits=precision_digits,
                )
                != -1
            ):
                continue
            move_to_cancel_vals = move._prepare_move_split_vals(
                quantity_todo - quantity_done
            )
            moves_to_cancel = (
                move.main_move_id._get_all_not_done_additional_moves()
                + move.copy(move_to_cancel_vals)
                - move
            )
            # moves to cancel may be linked to done preparation moves.
            # the propagation of the cancel action will cause a cancel on them
            # we force cancel to avoid blockage on cancel permission
            moves_to_cancel.with_context(force_cancel=True)._action_cancel()
            move.product_uom_qty = quantity_done

    def _action_confirm(self, merge=True, merge_into=False):
        # The confirmation could lead to the call _action_assign on the moves
        # which could create additional moves. The creation of the additional
        # move will run the stock rule which will call the _action_confirm
        # on the additional move. We need to ensure that the merge mode is
        # preserved for the additional moves. This is required to avoid that
        # moves split when creating a backorder are merged in the original move.
        # also for the additional moves.
        original_env = self.env
        merge = self.env.context.get("allow_merge", merge)
        # we ensure that recursive calls are done with the same merge mode
        self_merge_allowed = self.with_context(allow_merge=merge)
        res = super(StockMove, self_merge_allowed)._action_confirm(merge, merge_into)
        # by resetting the environment we ensure that the context is restored to
        # the original value at the end of the recursive calls stack
        return res.with_env(original_env)
