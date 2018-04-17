# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class Picking(models.Model):

    _inherit = "stock.picking"

    @api.multi
    def _compute_helpdesk_tickets_count(self):
        for picking in self:
            domain = [
                ('stock_picking_id', '=', self.id)
            ]

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
        action_data['domain'] = [
            ('stock_picking_id', '=', self.id)
        ]

        return action_data
