# Copyright 2017 Camptocamp SA
# Copyright 2023 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError

from odoo.addons.account.models.account_move import AccountMove as MoveAccount
from odoo.addons.helpdesk.models.helpdesk_ticket import (
    HelpdeskTicket as Ticket,
    HelpdeskTicketType as TicketType,
)
from odoo.addons.product.models.product_product import ProductProduct as Product
from odoo.addons.purchase.models.purchase import PurchaseOrder as OrderPurchase
from odoo.addons.sale.models.sale_order import SaleOrder as OrderSale
from odoo.addons.stock.models.stock_location import Location
from odoo.addons.stock.models.stock_lot import StockLot as Lot
from odoo.addons.stock.models.stock_move import StockMove as MoveStock
from odoo.addons.stock.models.stock_picking import Picking


class HelpdeskTicketReason(models.Model):

    _name = "helpdesk.ticket.reason"
    _description = "Ticket Reason"
    _order = "name asc"

    name = fields.Char(string="Name", translate=True, required=True)
    visible_reception_wizard = fields.Boolean("Visible on Reception Wizard?")
    location_dest_id = fields.Many2one[Location](
        string="Destination Location", ondelete="restrict"
    )


class HelpdeskTicket(Ticket):

    name = fields.Char(default="/")
    ticket_type_id = fields.Many2one[TicketType](
        default=lambda self: self.env.ref("helpdesk.type_incident")
    )
    helpdesk_ticket_reason_id = fields.Many2one[HelpdeskTicketReason](string="Reason")
    stock_picking_id = fields.Many2one[Picking](string="Stock picking")
    stock_move_id = fields.Many2one[MoveStock](string="Stock move", index=True)
    lots = fields.Many2one[Lot](
        related="stock_move_id.move_line_ids.lot_id", readonly=True
    )
    sale_order_id = fields.Many2one[OrderSale](string="Sale order")
    purchase_order_id = fields.Many2one[OrderPurchase](string="Purchase order")
    account_move_id = fields.Many2one[MoveAccount](string="Invoice")
    product_id = fields.Many2one[Product](string="Product")

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
            qty_ordered = 0
            qty_received = 0
            if not rec.product_id or not rec.purchase_order_id:
                rec.qty_ordered = qty_ordered
                rec.qty_received = qty_received
                return
            for line in rec.purchase_order_id.order_line:
                if line.product_id == rec.product_id:
                    qty_ordered += line.product_qty
                    qty_received += line.qty_received
            rec.qty_ordered = qty_ordered
            rec.qty_received = qty_received

    @api.constrains("helpdesk_ticket_reason_id")
    def _check_helpdesk_ticket_reason_id(self):
        if any(not rec.helpdesk_ticket_reason_id for rec in self):
            raise UserError(_("The ticket reason is mandatory."))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "/") == "/":
                sequence = self.env.ref("alce_helpdesk.seq_ticket_auto")
                vals["name"] = sequence.next_by_id()
        res = super().create(vals_list)
        for ticket in res:
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
        return res

    @api.model
    def new_one(self, r):
        """Return the action for the wizard to create a new ticket."""
        view = self.env.ref("alce_helpdesk.create_helpdesk_ticket_view_form")
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
