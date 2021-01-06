# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class Picking(models.Model):

    _inherit = "stock.picking"

    @api.multi
    def _compute_helpdesk_tickets_count(self):
        for picking in self:
            domain = [("stock_picking_id", "=", picking.id)]
            picking.helpdesk_tickets_count = len(
                self.env["helpdesk.ticket"].search(domain)
            )

    helpdesk_tickets_count = fields.Integer(compute="_compute_helpdesk_tickets_count")

    @api.multi
    def action_view_helpdesk_tickets(self):
        self.ensure_one()
        action_data = self.env.ref("helpdesk.helpdesk_ticket_action_main_tree").read()[
            0
        ]
        context = eval(action_data.get("context", "{}"))
        context["default_team_id"] = self.env.ref("alc_oeel_helpdesk.supplier_team").id
        action_data["context"] = str(context)
        action_data["domain"] = [("stock_picking_id", "=", self.id)]
        return action_data

    @api.multi
    def helpdesk_ticket_clicked(self):
        """Show existing ticket or offer to create a new one"""
        self.ensure_one()
        if self.helpdesk_tickets_count == 0:
            r = self.env["create.helpdesk.ticket"].create()
            return self.env["helpdesk.ticket"].new_one(r)
        else:
            return self.env["helpdesk.ticket"].show_existing(
                [("stock_picking_id", "=", self.id)]
            )
