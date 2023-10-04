# Copyright 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _
from odoo.exceptions import UserError

from odoo.addons.stock_picking_back2draft.models.stock_move import StockMove


class Move(StockMove):
    def _action_cancel(self):
        """Prevent to cancel a move from a printed picking."""
        if self.filtered("picking_id.printed") and not self.env.context.get(
            "force_cancel"
        ):
            raise UserError(
                _("You cannot cancel a move that is part of a started picking")
            )
        return super()._action_cancel()
