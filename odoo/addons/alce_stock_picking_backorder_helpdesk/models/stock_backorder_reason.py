# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV

from odoo import fields, models


class StockBackorderReason(models.Model):

    _inherit = "stock.backorder.reason"

    is_helpdesk_ticket_to_create = fields.Boolean(string="Create helpdesk ticket")
    helpdesk_ticket_reason_id = fields.Many2one(
        comodel_name="helpdesk.ticket.reason",
        string="Helpdesk ticket reason",
        ondelete="restrict",
    )
