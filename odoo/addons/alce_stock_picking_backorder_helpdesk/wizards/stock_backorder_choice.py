# Copyright 2021 ACSONE SA/NV

from odoo import fields

from odoo.addons.alce_helpdesk.models.helpdesk_ticket import HelpdeskTicketReason
from odoo.addons.stock_picking_backorder_reason.wizards.stock_backorder_reason_choice import (
    StockBackorderReasonChoice as BackorderReasonChoice,
)


class StockBackorderChoice(BackorderReasonChoice):

    is_helpdesk_ticket_to_create = fields.Boolean(
        related="reason_id.is_helpdesk_ticket_to_create", readonly=True
    )
    helpdesk_ticket_reason_id = fields.Many2one[HelpdeskTicketReason](
        related="reason_id.helpdesk_ticket_reason_id", readonly=True, ondelete="cascade"
    )
    helpdesk_ticket_description = fields.Char(string="Helpdesk ticket description")

    def _get_helpdesk_ticket_values(self):
        po = self.env["purchase.order"].search(
            [("name", "=", self.picking_ids.origin)], limit=1
        )
        return {
            "description": self.helpdesk_ticket_description,
            "helpdesk_ticket_reason_id": self.helpdesk_ticket_reason_id.id,
            "stock_picking_id": self.picking_ids.id,
            "partner_id": self.picking_ids.partner_id.id,
            "purchase_order_id": po and po.id or False,
        }

    def apply(self):
        self.ensure_one()
        if self.is_helpdesk_ticket_to_create:
            self.env["helpdesk.ticket"].create(self._get_helpdesk_ticket_values())
        return super().apply()
