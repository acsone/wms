# Copyright 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _
from odoo.exceptions import UserError

from odoo.addons.stock_picking_back2draft.models.stock_picking import StockPicking


class Picking(StockPicking):
    def action_cancel(self):
        """
        Restrict picking cancel in such cases:

        - We are in 'internal' and 'outgoing' pickings
        - User has no rights to cancel
        - Cancel is forced in context
        """
        # Don't browse pickings if we have these contexts
        if self.user_has_groups(
            "alc_stock_picking_cancel_permission.group_picking_cancel"
        ) or self.env.context.get("force_cancel"):
            return super().action_cancel()
        codes = self.mapped("picking_type_code")
        if "outgoing" in codes or "internal" in codes:
            raise UserError(_("You are not allowed to cancel such operation"))
        return super().action_cancel()
