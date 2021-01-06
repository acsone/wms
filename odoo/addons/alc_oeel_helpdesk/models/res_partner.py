# -*- coding: utf-8 -*-
# Copyright 2017 Julien Coux (Camptocamp)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.multi
    def _compute_helpdesk_tickets_count(self):
        for partner in self:
            domain = [("partner_id", "=", partner.id)]

            partner.helpdesk_tickets_count = len(
                self.env["helpdesk.ticket"].search(domain)
            )

    helpdesk_tickets_count = fields.Integer(compute="_compute_helpdesk_tickets_count")

    @api.multi
    def action_view_helpdesk_tickets(self):
        self.ensure_one()
        action_data = self.env.ref("helpdesk.helpdesk_ticket_action_main_tree").read()[
            0
        ]
        action_data["domain"] = [("partner_id", "=", self.id)]
        return action_data
