# Copyright 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields
from odoo.exceptions import UserError

from odoo.addons.stock_picking_back2draft.models.stock_picking import StockPicking


class Picking(StockPicking):

    alc_should_raise_cancel_error = fields.Boolean(
        compute="_compute_alc_should_raise_cancel_error",
        help="This indicates that the record should raise an error in case of cancellation."
        "(Based currently on picking types codes)",
    )

    @api.model
    def _check_alc_can_bypass_cancel_permission(self) -> bool:
        return bool(
            self.user_has_groups(
                "alc_stock_picking_cancel_permission.group_picking_cancel"
            )
            or self.env.context.get("force_cancel")
        )

    @api.depends("picking_type_code")
    def _compute_alc_should_raise_cancel_error(self):
        """If picking type is outgoing or internal, the cancel user error should raise."""
        should_raise = set()
        should_not_raise = set()
        for picking in self:
            if (
                "outgoing" in picking.picking_type_code
                or "internal" in picking.picking_type_code
            ):
                should_raise.add(picking.id)
            else:
                should_not_raise.add(picking.id)
        self.browse(should_raise).update({"alc_should_raise_cancel_error": True})
        self.browse(should_not_raise).update({"alc_should_raise_cancel_error": False})

    def action_cancel(self):
        """
        Restrict picking cancel in such cases:

        - We are in 'internal' and 'outgoing' pickings
        - User has no rights to cancel
        - Cancel is forced in context
        """
        # Don't browse pickings if we have these contexts
        if self._check_alc_can_bypass_cancel_permission():
            return super().action_cancel()
        for picking in self:
            if picking.alc_should_raise_cancel_error:
                raise UserError(
                    _(
                        "You are not allowed to cancel such operation (Picking: %(picking_name)s)",
                        picking_name=picking.name,
                    )
                )
        return super().action_cancel()
