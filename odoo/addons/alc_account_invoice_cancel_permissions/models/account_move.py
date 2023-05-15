# Copyright 2022 ACSONE SA/V
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields
from odoo.exceptions import AccessError

from odoo.addons.account.models.account_move import AccountMove as AccountMoveBase


class AccountMove(AccountMoveBase):

    action_invoice_cancel_allowed = fields.Boolean(
        default=False, compute="_compute_action_invoice_cancel_allowed"
    )

    @api.depends("state", "move_type")
    def _compute_action_invoice_cancel_allowed(self):
        user_can_cancel_invoices = self.env.user.has_group(
            "alc_account_invoice_cancel_permissions.cancel_invoice_permission"
        )
        for rec in self:
            if rec.move_type == "entry" or (
                user_can_cancel_invoices and rec.state == "draft"
            ):
                rec.action_invoice_cancel_allowed = True
            else:
                rec.action_invoice_cancel_allowed = False

    def button_cancel_check(self):
        if self.filtered(lambda r: not r.action_invoice_cancel_allowed):
            raise AccessError(
                _(
                    "You are not allowed to cancel invoices. Check user permissions and the state of the invoice."
                )
            )

    def button_cancel(self):
        self.button_cancel_check()
        return super().button_cancel()
