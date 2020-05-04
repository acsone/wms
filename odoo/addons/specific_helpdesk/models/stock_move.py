# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class StockMove(models.Model):

    _inherit = "stock.move"

    @api.multi
    def _compute_helpdesk_tickets_count(self):
        for move in self:
            domain = [("stock_move_id", "=", move.id)]
            move.helpdesk_tickets_count = len(
                self.env["helpdesk.ticket"].search(domain)
            )

    helpdesk_tickets_count = fields.Integer(compute="_compute_helpdesk_tickets_count")

    @api.multi
    def helpdesk_ticket_clicked(self):
        """Show existing ticket or offer to create a new one"""
        self.ensure_one()
        if self.helpdesk_tickets_count == 0:
            r = self.env["create.helpdesk.ticket"].create()
            return self.env["helpdesk.ticket"].new_one(r)
        else:
            return self.env["helpdesk.ticket"].show_existing(
                [("stock_move_id", "=", self.id)]
            )
