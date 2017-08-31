# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockBackorderReason(models.Model):
    _name = 'stock.backorder.reason'
    _order = 'name'

    name = fields.Char(
        string='Name',
        required=True,
    )

    backorder_action_to_do = fields.Selection(
        selection=[
            ('create', 'Create backorder'),
            ('cancel', 'Cancel backorder'),
            (
                'use_partner_option',
                'Use partner option (Purchase back order accepted)'
            ),
        ],
        string='Backorder action to do',
    )

    is_helpdesk_ticket_to_create = fields.Boolean(
        string='Is helpdesk ticket to create?',
    )

    helpdesk_ticket_reason_id = fields.Many2one(
        comodel_name='helpdesk.ticket.reason',
        string='Helpdesk ticket reason',
    )

    helpdesk_ticket_default_name = fields.Char(
        string='Helpdesk ticket defaut name',
        help='The default name to use for create a helpdesk ticket.',
    )
