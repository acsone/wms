# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.stock_picking_backorder_reason.models.stock_picking import (
    StockPicking as StockPickingBase,
)


class StockPicking(StockPickingBase):
    def button_validate(self):
        if self.env.context.get("release_channel_deliver_skip_backorder_reason"):
            # we manually escaped backorder reason, we need to apply partner
            # choice for backorder cancellation
            # the creation choice is the normal use case
            pickings_with_backorder = self._check_backorder()
            picking_ids_not_to_backorder = pickings_with_backorder.filtered(
                lambda picking: picking.backorder_reason_strategy == "cancel"
            )
            return super(
                StockPicking,
                self.with_context(
                    picking_ids_not_to_backorder=picking_ids_not_to_backorder.ids
                ),
            ).button_validate()
        return super().button_validate()
