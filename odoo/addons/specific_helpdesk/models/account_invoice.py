# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class AccountInvoice(models.Model):

    _inherit = "account.invoice"

    helpdesk_tickets_count = fields.Integer(compute="_compute_helpdesk_tickets_count")

    @api.multi
    def _compute_helpdesk_tickets_count(self):
        for invoice in self:
            domain = [("account_invoice_id", "=", invoice.id)]
            invoice.helpdesk_tickets_count = len(
                self.env["helpdesk.ticket"].search(domain)
            )

    @api.multi
    def action_view_helpdesk_tickets(self):
        self.ensure_one()
        action_data = self.env.ref("helpdesk.helpdesk_ticket_action_main_tree").read()[
            0
        ]
        context = eval(action_data.get("context", "{}"))
        context["default_team_id"] = self.env.ref(
            "specific_helpdesk.accounting_team"
        ).id
        action_data["context"] = str(context)
        action_data["domain"] = [("account_invoice_id", "=", self.id)]
        return action_data
