# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/V
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import AccessError


class AccountInvoice(models.Model):

    _inherit = "account.invoice"

    action_invoice_cancel_allowed = fields.Boolean(
        default=False, compute="_compute_action_invoice_cancel_allowed"
    )

    @api.depends("state")
    def _compute_action_invoice_cancel_allowed(self):
        user_can_cancel_invoices = self.env.user.has_group(
            "alc_account_invoice_cancel_permissions.cancel_invoice_permission"
        )
        for rec in self:
            if user_can_cancel_invoices and rec.state in ("proforma2", "draft", "open"):
                rec.action_invoice_cancel_allowed = True
            else:
                rec.action_invoice_cancel_allowed = False

    def action_invoice_cancel_check(self):
        if self.filtered(lambda r: not r.action_invoice_cancel_allowed):
            msg = "You are not allowed to cancel invoices. Check user permissions and the state of the invoice."
            raise AccessError(_(msg))

    def action_invoice_cancel(self):
        self.action_invoice_cancel_check()
        return super(AccountInvoice, self).action_invoice_cancel()
