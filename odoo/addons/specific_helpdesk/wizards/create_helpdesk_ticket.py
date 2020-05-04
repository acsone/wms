# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class CreateHelpdeskTicket(models.TransientModel):
    _name = "create.helpdesk.ticket"

    helpdesk_ticket_reason_id = fields.Many2one(
        comodel_name="helpdesk.ticket.reason",
        string="Reason",
        # required=True,
    )
    description = fields.Char(string="Description")

    @api.multi
    def create_helpdesk_ticket(self):
        active_model = self._context.get("active_model")
        active_id = self._context.get("active_id")

        if not active_id:
            raise UserError(
                _("The record related to the new helpdesk" "ticket was not found !")
            )
        record = self.env[active_model].browse(active_id)
        if active_model == "stock.picking":
            picking = record
            stock_move_id = False
        else:
            stock_move_id = record.id
            picking = record.picking_id

        ticket = {
            "helpdesk_ticket_reason_id": self.helpdesk_ticket_reason_id.id,
            "name": self.description,
            "partner_id": picking.partner_id.id,
            "stock_picking_id": picking.id,
            "stock_move_id": stock_move_id,
            "product_id": picking.product_id.id,
        }

        env = self.env
        if picking.sale_id:
            ticket["sale_order_id"] = picking.sale_id.id
            ticket["team_id"] = env.ref("specific_helpdesk.customer_team").id
        if picking.purchase_id:
            ticket["purchase_order_id"] = picking.purchase_id.id
            ticket["team_id"] = env.ref("specific_helpdesk.supplier_team").id

        self.env["helpdesk.ticket"].create(ticket)
