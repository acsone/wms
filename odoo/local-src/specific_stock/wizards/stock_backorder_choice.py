# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class StockBackorderChoice(models.TransientModel):
    _name = 'stock.backorder.choice'

    picking_id = fields.Many2one(
        comodel_name='stock.picking',
        string='Picking',
        readonly=True,
    )

    backorder_confirmation_id = fields.Many2one(
        comodel_name='stock.backorder.confirmation',
        string='Backorder confirmation',
        readonly=True,
    )

    reason_id = fields.Many2one(
        comodel_name='stock.backorder.reason',
        string='Backorder reason',
        required=True,
    )

    backorder_action_to_do = fields.Selection(
        related='reason_id.backorder_action_to_do',
        readonly=True,
    )

    is_purchase_back_order_accepted = fields.Boolean(
        related='picking_id.partner_id.is_purchase_back_order_accepted',
        readonly=True,
    )

    is_helpdesk_ticket_to_create = fields.Boolean(
        related='reason_id.is_helpdesk_ticket_to_create',
        readonly=True,
    )

    helpdesk_ticket_reason_id = fields.Many2one(
        related='reason_id.helpdesk_ticket_reason_id',
        readonly=True,
    )

    helpdesk_ticket_name = fields.Char(
        string='Helpdesk ticket name',
        help='The name to use for create a helpdesk ticket.',
    )

    @api.onchange('reason_id')
    def onchange_type(self):
        self.helpdesk_ticket_name = self.reason_id.helpdesk_ticket_default_name

    def _get_helpdesk_ticket_values(self):
        return {
            'name': self.helpdesk_ticket_name,
            'helpdesk_ticket_reason_id': self.helpdesk_ticket_reason_id.id,
            'stock_picking_id': self.picking_id.id,
            'partner_id': self.picking_id.partner_id.id,
        }

    @api.multi
    def apply(self):
        self.ensure_one()
        if self.is_helpdesk_ticket_to_create:
            self.env['helpdesk.ticket'].create(
                self._get_helpdesk_ticket_values()
            )
        keep_backorder = (
            self.backorder_action_to_do == 'create' or
            (
                self.backorder_action_to_do == 'use_partner_option' and
                self.picking_id.partner_id.is_purchase_back_order_accepted
            )
        )
        if keep_backorder:
            self.backorder_confirmation_id.process()
        else:
            self.backorder_confirmation_id.process_cancel_backorder()
