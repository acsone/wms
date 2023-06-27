# Copyright 2018 Camptocamp SA
# Copyright 2023 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields
from odoo.tools.safe_eval import safe_eval

from odoo.addons.account.models.account_move import AccountMove as Move


class AccountInvoice(Move):

    helpdesk_tickets_count = fields.Integer(compute="_compute_helpdesk_tickets_count")

    def _compute_helpdesk_tickets_count(self):
        for move in self:
            domain = [("account_move_id", "=", move.id)]
            move.helpdesk_tickets_count = len(
                self.env["helpdesk.ticket"].search(domain)
            )

    def action_view_helpdesk_tickets(self):
        self.ensure_one()
        action_data = self.env.ref("helpdesk.helpdesk_ticket_action_main_tree").read()[
            0
        ]
        context = safe_eval(action_data.get("context", "{}"))
        context["default_team_id"] = self.env.ref("alce_helpdesk.accounting_team").id
        action_data["context"] = str(context)
        action_data["domain"] = [("account_move_id", "=", self.id)]
        return action_data
