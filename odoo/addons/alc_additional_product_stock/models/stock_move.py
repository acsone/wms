# Copyright 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import _, api, fields

from odoo.addons.stock_move_propagate_first_move.models.stock_move import (
    StockMove as StockMoveBase,
)

_logger = logging.getLogger(__name__)


class StockMove(StockMoveBase):

    is_additional_move = fields.Boolean(string="Is Additional Move")
    main_move_id = fields.Many2one[StockMoveBase](
        string="Main Product Move",
        ondelete="set null",
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
        return _("ADDITIONAL PRODUCT: %(ap_name)s (FROM %(m_p_name)s)") % dict(
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
        additional_moves_to_remove = self.filtered("is_additional_move")
        main_moves = self - additional_moves_to_remove
        main_moves._remove_all_additional_moves()
        res = super(StockMove, main_moves)._action_assign(force_qty=force_qty)
        main_moves._add_additional_products()
        return res

    def _action_cancel(self):
        additional_moves = self.mapped("additional_move_ids")
        if additional_moves:
            self.mapped("additional_move_ids")._action_cancel()
        return super()._action_cancel()

    def _get_all_not_done_additional_moves(self):
        if not self.is_additional_move:
            first_move = self.first_move_id
            first_additional_move = first_move.additional_move_ids
            return (
                self.search(
                    [
                        ("first_move_id", "in", first_additional_move.ids),
                        ("state", "!=", "done"),
                    ]
                )
                | first_additional_move
            )
        return self.browse()

    def _remove_all_additional_moves(self):
        for move in self:
            if not move.additional_product_on_reserved_qty_allowed:
                continue
            moves_to_remove = move._get_all_not_done_additional_moves()
            if moves_to_remove:
                moves_to_remove._action_cancel()
                moves_to_remove.sudo().unlink()

    @api.model
    def _prepare_merge_moves_distinct_fields(self):
        return super()._prepare_merge_moves_distinct_fields() + [
            "main_move_id",
            "is_additional_move",
        ]
