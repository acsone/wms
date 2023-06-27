# Copyright 2021 ACSONE SA/NV

from odoo import fields

from odoo.addons.alce_helpdesk.models.helpdesk_ticket import HelpdeskTicketReason
from odoo.addons.stock_picking_backorder_reason.models.stock_backorder_reason import (
    StockBackorderReason as BackorderReason,
)


class StockBackorderReason(BackorderReason):

    is_helpdesk_ticket_to_create = fields.Boolean(string="Create helpdesk ticket")
    helpdesk_ticket_reason_id = fields.Many2one[HelpdeskTicketReason](
        string="Helpdesk ticket reason",
        ondelete="restrict",
    )
