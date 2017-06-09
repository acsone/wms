# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class HelpdeskTicket(models.Model):

    _inherit = 'helpdesk.ticket'

    helpdesk_ticket_reason_id = fields.Many2one(
        comodel_name='helpdesk.ticket.reason', string='Reason')


class HelpdeskTicketReason(models.Model):

    _name = 'helpdesk.ticket.reason'
    _description = 'Ticket Reason'

    name = fields.Char(string='Name')
