# Copyright 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api
from odoo.exceptions import UserError

from odoo.addons.stock_picking_back2draft.models.stock_move import StockMove


class Move(StockMove):
    @api.model
    def _check_alc_can_bypass_cancel_permission(self) -> bool:
        return bool(
            self.user_has_groups(
                "alc_stock_picking_cancel_permission.group_picking_cancel"
            )
            or self.env.context.get("force_cancel")
            or self.env.context.get("cancel_backorder")
        )

    def _action_cancel(self):
        """Prevent to cancel a move from a printed picking."""
        if self._check_alc_can_bypass_cancel_permission():
            return super()._action_cancel()
        started_pickings = self.picking_id.filtered(
            lambda p: p.alc_should_raise_cancel_error and p.printed
        )
        if started_pickings:
            raise UserError(
                _(
                    "This action is not allowed because it leads to the cancellation of"
                    " a move of a started picking.\n%(pickings)s",
                    pickings=", ".join(started_pickings.mapped("display_name")),
                )
            )
        return super()._action_cancel()
