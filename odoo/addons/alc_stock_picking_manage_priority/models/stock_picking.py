# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields
from odoo.exceptions import ValidationError

from odoo.addons.stock.models.stock_picking import Picking


class StockPicking(Picking):

    is_priority_editable = fields.Boolean(
        compute="_compute_is_priority_editable",
    )

    priority = fields.Selection(tracking=True)

    @api.depends("company_id.stock_move_manage_priority", "is_locked", "state")
    def _compute_is_priority_editable(self):
        user_has_group = self.env.user.has_group(
            "stock_move_manage_priority.group_stock_move_priority_manager"
        )
        for rec in self:
            rec.is_priority_editable = (
                user_has_group
                and not rec.is_locked
                and rec.state not in ("done", "cancel")
                and rec.company_id.stock_move_manage_priority
            )

    def write(self, vals):
        no_check_priority = self.env.context.get("no_check_priority")
        if (
            "priority" in vals
            and not no_check_priority
            and any(not picking.is_priority_editable for picking in self)
        ):
            raise ValidationError(_("You don't have the right to change the priority."))
        return super(StockPicking, self.with_context(no_check_priority=False)).write(
            vals
        )

    def _action_done(self):
        """
        The priority is set to 0 in the original _action_done so we need to bypass.

        the check or no picking validation can be done
        """
        return super(
            StockPicking, self.with_context(no_check_priority=True)
        )._action_done()
