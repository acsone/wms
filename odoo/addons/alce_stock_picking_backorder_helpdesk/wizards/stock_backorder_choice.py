# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV

from odoo import fields, models


class StockBackorderChoice(models.TransientModel):

    _inherit = "stock.backorder.choice"

    is_helpdesk_ticket_to_create = fields.Boolean(
        related="reason_id.is_helpdesk_ticket_to_create", readonly=True
    )
    helpdesk_ticket_reason_id = fields.Many2one(
        related="reason_id.helpdesk_ticket_reason_id", readonly=True, ondelete="cascade"
    )
    helpdesk_ticket_description = fields.Char(string="Helpdesk ticket description")

    def _get_helpdesk_ticket_values(self):
        po = self.env["purchase.order"].search(
            [("name", "=", self.picking_id.origin)], limit=1
        )
        return {
            "description": self.helpdesk_ticket_description,
            "helpdesk_ticket_reason_id": self.helpdesk_ticket_reason_id.id,
            "stock_picking_id": self.picking_id.id,
            "partner_id": self.picking_id.partner_id.id,
            "purchase_order_id": po and po.id or False,
        }

    def apply(self):
        self.ensure_one()
        if self.is_helpdesk_ticket_to_create:
            self.env["helpdesk.ticket"].create(self._get_helpdesk_ticket_values())
        return super(StockBackorderChoice, self).apply()
