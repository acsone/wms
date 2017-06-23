# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class HelpdeskTicket(models.Model):

    _inherit = 'helpdesk.ticket'

    helpdesk_ticket_reason_id = fields.Many2one(
        comodel_name='helpdesk.ticket.reason', string='Reason')

    ref = fields.Reference(
        selection=[
            ('res.partner', 'Partner'),
            ('product.product', 'Product'),
            ('account.invoice', 'Invoice'),
            ('stock.production.lot', 'Lot/Serial number'),
            ('mrp.repair', 'Repair'),
        ],
        string='Reference')

    stock_picking_id = fields.Many2one(comodel_name='stock.picking',
                                       string='Picking')

    @api.model
    def default_get(self, fields):
        res = super(HelpdeskTicket, self).default_get(fields)
        logistics_type = self.env.ref('specific_helpdesk.type_logistics')
        if (self._context.get('type') == logistics_type.id and
                self._context.get('stock_picking')):
            res['ticket_type_id'] = logistics_type.id
            res['stock_picking_id'] = self._context.get('stock_picking')
        return res

    @api.model
    def create(self, vals):
        ticket = super(HelpdeskTicket, self).create(vals)
        if ticket.partner_id.user_id.partner_id:
            ticket.message_subscribe(
                partner_ids=ticket.partner_id.user_id.partner_id.ids
            )

        return ticket


class HelpdeskTicketReason(models.Model):

    _name = 'helpdesk.ticket.reason'
    _description = 'Ticket Reason'

    name = fields.Char(string='Name')
