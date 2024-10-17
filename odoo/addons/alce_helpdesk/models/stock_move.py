# Copyright 2018 Camptocamp SA
# Copyright 2023 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields

from odoo.addons.stock.models.stock_move import StockMove as Move


class StockMove(Move):
    def _compute_helpdesk_tickets_count(self):
        for move in self:
            domain = [("stock_move_id", "=", move.id)]
            move.helpdesk_tickets_count = len(
                self.env["helpdesk.ticket"].search(domain)
            )

    helpdesk_tickets_count = fields.Integer(compute="_compute_helpdesk_tickets_count")

    def helpdesk_ticket_clicked(self):
        """Show existing ticket or offer to create a new one."""
        self.ensure_one()
        if not self.helpdesk_tickets_count:
            r = self.env["create.helpdesk.ticket"].create()
            return self.env["helpdesk.ticket"].new_one(r)
        return self.env["helpdesk.ticket"].show_existing(
            [("stock_move_id", "=", self.id)]
        )
