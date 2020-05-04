# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class HelpdeskTicket(models.Model):

    _inherit = "helpdesk.ticket"

    name = fields.Char(default="/")
    ticket_type_id = fields.Many2one(
        default=lambda self: self.env.ref("helpdesk.type_incident")
    )
    helpdesk_ticket_reason_id = fields.Many2one(
        comodel_name="helpdesk.ticket.reason", string="Reason", required=True
    )
    stock_picking_id = fields.Many2one(
        comodel_name="stock.picking", string="Stock picking"
    )
    stock_move_id = fields.Many2one(comodel_name="stock.move", string="Stock move")
    lots = fields.Many2one(related="stock_move_id.quant_ids.lot_id")
    sale_order_id = fields.Many2one(comodel_name="sale.order", string="Sale order")
    purchase_order_id = fields.Many2one(
        comodel_name="purchase.order", string="Purchase order"
    )
    account_invoice_id = fields.Many2one(
        comodel_name="account.invoice", string="Invoice"
    )
    product_id = fields.Many2one(comodel_name="product.product", string="Product")

    # fields for email templates
    qty_ordered = fields.Float(
        string="Ordered product quantitiy",
        compute="_compute_purchase_qty",
        readonly=True,
    )
    qty_received = fields.Float(
        string="Received product quantitiy",
        compute="_compute_purchase_qty",
        readonly=True,
    )

    @api.depends(
        "product_id",
        "purchase_order_id.order_line.product_qty",
        "purchase_order_id.order_line.qty_received",
    )
    def _compute_purchase_qty(self):
        for rec in self:
            if not rec.product_id or not rec.purchase_order_id:
                return
            qty_ordered = 0
            qty_received = 0
            for line in rec.purchase_order_id.order_line:
                if line.product_id == rec.product_id:
                    qty_ordered += line.product_qty
                    qty_received += line.qty_received
            rec.qty_ordered = qty_ordered
            rec.qty_received = qty_received

    @api.model
    def create(self, vals):
        if vals.get("name", "/") == "/":
            sequence = self.env.ref("specific_helpdesk.seq_ticket_auto")
            vals["name"] = sequence.next_by_id()
        ticket = super(HelpdeskTicket, self).create(vals)

        partners_to_add = []
        if ticket.partner_id.commercial_partner_id.user_id.partner_id:
            partners_to_add.append(
                ticket.partner_id.commercial_partner_id.user_id.partner_id.id
            )
        if ticket.partner_id.purchase_manager_id.partner_id:
            partners_to_add.append(ticket.partner_id.purchase_manager_id.partner_id.id)
        if partners_to_add:
            ticket.message_subscribe(partner_ids=partners_to_add)
        return ticket

    @api.model
    def new_one(self, r):
        """Return the action for the wizard to create a new ticket."""
        view = self.env.ref("specific_helpdesk.create_helpdesk_ticket_view_form")
        return {
            "type": "ir.actions.act_window",
            "res_model": "create.helpdesk.ticket",
            "res_id": r.id,
            "view_id": view.id,
            "view_type": "form",
            "view_mode": "form",
            "target": "new",
        }

    @api.model
    def show_existing(self, domain):
        """Show the helpdesk tickets for a specific domain."""
        action_data = self.env.ref("helpdesk.helpdesk_ticket_action_main_tree").read()[
            0
        ]
        action_data["domain"] = domain
        return action_data


class HelpdeskTicketReason(models.Model):

    _name = "helpdesk.ticket.reason"
    _description = "Ticket Reason"

    name = fields.Char(string="Name", translate=True, required=True)
    visible_reception_wizard = fields.Boolean("Visible on Reception Wizard?")
    location_dest_id = fields.Many2one(
        "stock.location", "Destination Location", ondelete="restrict"
    )
