# Copyright 2023 Michael Tietz (MT Software) <mtietz@mt-software.de>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    is_full_location_reservation = fields.Boolean(
        "Full location reservation move", default=False
    )

    def _filter_full_location_reservation_moves(self):
        return self.filtered(lambda m: m.is_full_location_reservation)

    def _action_cancel(self):
        """
        Override the method to do the unlink only as the super() do
        the unreserve also.
        """
        # If we are already in a undo_full_location_reservation context,
        # we return super() method.
        if self.env.context.get("skip_undo_full_location_reservation"):
            return super()._action_cancel()
        new_self = self.with_context(skip_undo_full_location_reservation=True)
        res = super(StockMove, new_self)._action_cancel()
        full_location_moves = self._filter_full_location_reservation_moves()
        if full_location_moves:
            full_location_moves.unlink()
        return res

    def _do_unreserve(self):
        if self.env.context.get("skip_undo_full_location_reservation"):
            return super()._do_unreserve()
        full_location_moves = self._filter_full_location_reservation_moves()
        full_location_moves._undo_full_location_reservation()
        return super(StockMove, (self - full_location_moves))._do_unreserve()

    def undo_full_location_reservation(self):
        full_location_moves = self._filter_full_location_reservation_moves()
        full_location_moves._undo_full_location_reservation()

    def _undo_full_location_reservation(self):
        if not self.exists():
            return
        self = self.with_context(skip_undo_full_location_reservation=True)
        self._do_unreserve()
        self._action_cancel()
        self.unlink()

    def _prepare_full_location_reservation_package_level_vals(self, package):
        return {
            "package_id": package.id,
            "company_id": self.company_id.id,
        }

    def _full_location_reservation_create_package_level(self, package):
        return self.env["stock.package_level"].create(
            self._prepare_full_location_reservation_package_level_vals(package)
        )

    def _full_location_reservation_prepare_move_vals(
        self, product, qty, location, package=None
    ):
        self.ensure_one()
        package_level_id = False
        if package:
            package_level_id = self._full_location_reservation_create_package_level(
                package
            ).id
        return {
            "is_full_location_reservation": True,
            "product_uom_qty": qty,
            "name": product.name,
            "product_uom": product.uom_id.id,
            "product_id": product.id,
            "location_id": location.id,
            "location_dest_id": self.picking_id.location_dest_id.id,
            "picking_id": self.picking_id.id,
            "package_level_id": package_level_id,
        }

    def _full_location_reservation_create_move(
        self, product, qty, location, package=None
    ):
        new_move = self.copy(
            default=self._full_location_reservation_prepare_move_vals(
                product, qty, location, package
            )
        )
        self.ensure_one()
        if self.picking_type_id.merge_move_for_full_location_reservation:
            # To be able to be merged, the new move should use the same source location as
            # the original one.
            new_move.location_id = self.location_id
            self._do_unreserve()
            # Don't merge at confirm
            new_move._action_confirm(merge=False)
            merged_move = (
                (new_move | self)
                .with_context(skip_undo_full_location_reservation=True)
                ._merge_moves(merge_into=self)
            )
            # If the concerned product is not the one of the original move,
            # it hasn't been merged.
            if len(merged_move) > 1:
                return new_move
            return merged_move
        return new_move

    def _full_location_reservation(self, package_only=None):
        return self.move_line_ids._full_location_reservation(package_only)
