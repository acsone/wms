# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models, fields, api


class HelpdeskTicket(models.Model):

    _inherit = 'helpdesk.ticket'

    name = fields.Char(
        default='/'
    )
    ticket_type_id = fields.Many2one(
        default=lambda self: self.env.ref('helpdesk.type_incident')
    )
    helpdesk_ticket_reason_id = fields.Many2one(
        comodel_name='helpdesk.ticket.reason', string='Reason',
        required=True,
    )
    stock_picking_id = fields.Many2one(
        comodel_name='stock.picking',
        string='Stock picking',
    )
    stock_move_id = fields.Many2one(
        comodel_name='stock.move',
        string='Stock move',
    )
    lots = fields.Many2one(
        related='stock_move_id.quant_ids.lot_id'
    )
    sale_order_id = fields.Many2one(
        comodel_name='sale.order',
        string='Sale order',
    )
    purchase_order_id = fields.Many2one(
        comodel_name='purchase.order',
        string='Purchase order',
    )
    account_invoice_id = fields.Many2one(
        comodel_name='account.invoice',
        string='Invoice',
    )
    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product',
    )

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            sequence = self.env.ref('specific_helpdesk.seq_ticket_auto')
            vals['name'] = sequence.next_by_id()
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

    @api.model
    def new_one(self, r):
        """Return the action for the wizard to create a new ticket."""
        view = self.env.ref(
                'specific_helpdesk.create_helpdesk_ticket_view_form')
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'create.helpdesk.ticket',
            'res_id': r.id,
            'view_id': view.id,
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            }

    @api.model
    def show_existing(self, domain):
        """Show the helpdesk tickets for a specific domain."""
        action_data = self.env.ref(
            'helpdesk.helpdesk_ticket_action_main_tree'
        ).read()[0]
        action_data['domain'] = domain
        return action_data


class HelpdeskTicketReason(models.Model):

    _name = 'helpdesk.ticket.reason'
    _description = 'Ticket Reason'

    name = fields.Char(string='Name')
