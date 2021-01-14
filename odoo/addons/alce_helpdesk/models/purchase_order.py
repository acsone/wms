# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval


class PurchaseOrder(models.Model):

    _inherit = "purchase.order"

    @api.multi
    def _compute_helpdesk_tickets_count(self):
        for order in self:
            domain = [("purchase_order_id", "=", order.id)]

            order.helpdesk_tickets_count = len(
                self.env["helpdesk.ticket"].search(domain)
            )

    helpdesk_tickets_count = fields.Integer(compute="_compute_helpdesk_tickets_count")

    @api.multi
    def action_view_helpdesk_tickets(self):
        self.ensure_one()

        action_data = self.env.ref("helpdesk.helpdesk_ticket_action_main_tree").read()[
            0
        ]
        context = safe_eval(action_data.get("context", "{}"))
        context["default_team_id"] = self.env.ref("alce_helpdesk.supplier_team").id
        action_data["context"] = str(context)
        action_data["domain"] = [("purchase_order_id", "=", self.id)]

        return action_data
