# Copyright 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, fields

from odoo.addons.stock.models.stock_move import StockMove as StockMoveBase


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

    def assign_picking(self):
        # Prevent any backorder of additional moves
        other_moves = self.browse()
        for move in self:
            # We are creating a backorder
            if move.picking_id and move.is_additional_move:
                move.with_context(
                    no_recompute_pack=True, force_cancel=True
                ).action_cancel()
                move.picking_id.message_post(
                    body=_("Remaining additional move '%s' canceled") % move.name
                )
            else:
                other_moves |= move
        if other_moves:
            return super(StockMove, other_moves).assign_picking()
        return True

    def split(self, qty, restrict_lot_id=False, restrict_partner_id=False):
        # Prevent any partial backorder of additional moves
        new_move_id = super().split(
            qty,
            restrict_lot_id=restrict_lot_id,
            restrict_partner_id=restrict_partner_id,
        )
        if self.is_additional_move and new_move_id:
            new_move = self.browse(new_move_id)
            new_move.with_context(
                no_recompute_pack=True, force_cancel=True
            ).action_cancel()
            return False
        return new_move_id

    def _get_moves_to_auto_reassign(self):
        """Overload the method from 'stock_reassign_auto' module to not.

        process products related to additional moves.
        """
        moves = super()._get_moves_to_auto_reassign()
        return moves.filtered(lambda m: not m.is_additional_move)

    def action_cancel(self):
        for rec in self:
            additional_products_to_cancel = rec.mapped(
                "product_id.additional_product_id"
            )
            if additional_products_to_cancel:
                for additional_product in additional_products_to_cancel:
                    moves_to_cancel = rec.search(
                        [
                            ("product_id", "=", additional_product.id),
                            ("state", "not in", ("cancel", "done")),
                            ("picking_id", "=", rec.picking_id.id),
                            ("is_additional_move", "=", True),
                            ("procurement_id", "=", rec.procurement_id.id),
                        ]
                    )
                    moves_to_cancel.with_context(
                        no_recompute_pack=True, force_cancel=True
                    ).action_cancel()
        return super().action_cancel()
