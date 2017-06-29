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
            ('stock.picking', 'Picking'),
            ('stock.production.lot', 'Lot/Serial number'),
            ('mrp.repair', 'Repair'),
        ],
        string='Reference')

    sale_order_id = fields.Many2one(
        comodel_name='sale.order',
        string='Sale order',
    )

    purchase_order_id = fields.Many2one(
        comodel_name='purchase.order',
        string='Purchase order',
    )

    @api.model
    def create(self, vals):
        ticket = super(HelpdeskTicket, self).create(vals)

        partners_to_add = []
        if ticket.partner_id.commercial_partner_id.user_id.partner_id:
            partners_to_add.append(
                ticket.partner_id.commercial_partner_id.user_id.partner_id.id
            )
        if ticket.partner_id.purchase_manager_id.partner_id:
            partners_to_add.append(
                ticket.partner_id.purchase_manager_id.partner_id.id
            )
        if partners_to_add:
            ticket.message_subscribe(partner_ids=partners_to_add)

        return ticket


class HelpdeskTicketReason(models.Model):

    _name = 'helpdesk.ticket.reason'
    _description = 'Ticket Reason'

    name = fields.Char(string='Name')
