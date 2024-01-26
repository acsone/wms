# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _
from odoo.exceptions import UserError

from odoo.addons.stock.models.stock_move import StockMove as StockMoveBase


class StockMove(StockMoveBase):
    def _check_expired_lot(self):
        """In any case, check that the config is coherent when processing an expired lot."""
        for rec in self:
            bad_lots = []
            for lot in rec.move_line_ids.lot_id:
                if (
                    rec.picking_type_id.no_expired_reservation_allowed
                    and not rec.picking_id.to_process_quant_expired
                    and lot.use_expiration_date
                    and lot.removal_date
                    and rec.picking_id.scheduled_date
                    and lot.removal_date < rec.picking_id.scheduled_date
                ):
                    bad_lots.append(f"{lot.name} {lot.removal_date}")
            if bad_lots:
                raise UserError(
                    _(
                        "You cannot transfer lots with a removal date:\n\t- %(lots)s",
                        lots="\n\t- ".join(bad_lots),
                    )
                )

    def _action_done(self, cancel_backorder=False):
        self._check_expired_lot()
        return super()._action_done(cancel_backorder=cancel_backorder)

    def _get_available_quantity(
        self,
        location_id,
        lot_id=None,
        package_id=None,
        owner_id=None,
        strict=False,
        allow_negative=False,
    ):
        self.ensure_one()
        move = self
        if (
            self.picking_type_id.no_expired_reservation_allowed
            and self.product_id.use_expiration_date
            and not self.picking_id.to_process_quant_expired
        ):
            move = self.with_context(removal_date_limit=self.picking_id.scheduled_date)
        return super(StockMove, move)._get_available_quantity(
            location_id,
            lot_id=lot_id,
            package_id=package_id,
            owner_id=owner_id,
            strict=strict,
            allow_negative=allow_negative,
        )

    def _update_reserved_quantity(
        self,
        need,
        available_quantity,
        location_id,
        lot_id=None,
        package_id=None,
        owner_id=None,
        strict=True,
    ):
        self.ensure_one()
        move = self
        if (
            self.picking_type_id.no_expired_reservation_allowed
            and self.product_id.use_expiration_date
            and not self.picking_id.to_process_quant_expired
        ):
            move = self.with_context(removal_date_limit=self.picking_id.scheduled_date)
        return super(StockMove, move)._update_reserved_quantity(
            need,
            available_quantity,
            location_id,
            lot_id=lot_id,
            package_id=package_id,
            owner_id=owner_id,
            strict=strict,
        )
