# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields, api
from odoo.tools.safe_eval import safe_eval


class Picking(models.Model):

    _inherit = "stock.picking"

    helpdesk_ticket_ids = fields.One2many(comodel_name='helpdesk.ticket',
                                          inverse_name='stock_picking_id',
                                          string='Helpdesk Tickets')
    helpdesk_tickets_count = fields.Integer(
        string='Tickets number', compute='_compute_helpdesk_tickets_count')

    @api.depends('helpdesk_ticket_ids')
    def _compute_helpdesk_tickets_count(self):
        for picking in self:
            picking.helpdesk_tickets_count = len(picking.helpdesk_ticket_ids)

    @api.multi
    def action_view_tickets(self):
        '''
        This function returns an action that display existing tickets
        of given stock picking ids. It can either be a in a list or in a form
        view, if there is only one delivery order to show.
        Moreover it adds context key so that a newly created Ticket is
         automatically linked to the stock.picking with type Logistics
        '''

        action = self.env.ref(
            'helpdesk.helpdesk_ticket_action_main_tree').read()[0]

        tickets = self.mapped('helpdesk_ticket_ids')
        if len(tickets) > 1 or not tickets:
            action['domain'] = [('id', 'in', tickets.ids)]
        elif tickets:
            action['views'] = [
                (self.env.ref('helpdesk.helpdesk_ticket_view_form').id,
                 'form')]
            action['res_id'] = tickets.id
        context = action.get('context', False)
        if not context:
            context = {}
        if not isinstance(context, dict):
            context = safe_eval(context)
        context.update({
            'type': self.env.ref('specific_helpdesk.type_logistics').id,
            'stock_picking': self.id
        })
        action['context'] = context
        return action
