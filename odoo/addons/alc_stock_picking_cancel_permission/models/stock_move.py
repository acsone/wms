# Copyright 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _
from odoo.exceptions import UserError

from odoo.addons.stock_picking_back2draft.models.stock_move import StockMove


class Move(StockMove):
    def _action_cancel(self):
        """Prevent to cancel a move from a printed picking."""
        if self.env.context.get("force_cancel") or self.env.context.get(
            "cancel_backorder"
        ):
            return super()._action_cancel()
        started_pickings = self.picking_id.filtered("printed")
        if started_pickings:
            raise UserError(
                _(
                    "This action is not allowed because it leads to the cancellation of"
                    " a move of a started picking.\n%(pickings)s",
                    pickings=", ".join(started_pickings.mapped("display_name")),
                )
            )
        return super()._action_cancel()
