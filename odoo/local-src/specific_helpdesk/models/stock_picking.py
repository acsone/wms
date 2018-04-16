# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class Picking(models.Model):

    _inherit = "stock.picking"

    @api.multi
    def _compute_helpdesk_tickets_count(self):
        for picking in self:
            domain = [('stock_picking_id', '=', picking.id)]
            picking.helpdesk_tickets_count = len(
                self.env['helpdesk.ticket'].search(domain)
            )

    helpdesk_tickets_count = fields.Integer(
        compute='_compute_helpdesk_tickets_count'
    )

    @api.multi
    def action_view_helpdesk_tickets(self):
        self.ensure_one()
        action_data = self.env.ref(
            'helpdesk.helpdesk_ticket_action_main_tree'
        ).read()[0]
        context = "{'search_default_is_open': True, 'default_team_id': %s}"
        action_data['domain'] = [('stock_picking_id', '=', self.id)]
        action_data['context'] = context % self.env.ref(
                'specific_helpdesk.accounting_team').id
        return action_data

    @api.multi
    def helpdesk_ticket_clicked(self):
        """Show existing ticket or offer to create a new one"""
        self.ensure_one()
        if self.helpdesk_tickets_count == 0:
            r = self.env['create.helpdesk.ticket'].create({
                'stock_picking_id': self.id
            })
            return self.env['helpdesk.ticket'].new_one(r)
        else:
            return self.env['helpdesk.ticket'].show_existing(
                [('stock_picking_id', '=', self.id)])
