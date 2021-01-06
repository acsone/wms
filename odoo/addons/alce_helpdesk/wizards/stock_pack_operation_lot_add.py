# -*- coding: utf-8 -*-
# Copyright 2017-2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

from odoo import _, api, fields, models


class StockPackOperationLotAdd(models.TransientModel):
    _inherit = "stock.pack.operation.lot.add"

    helpdesk_ticket_reason_id = fields.Many2one(
        comodel_name="helpdesk.ticket.reason",
        domain=[("visible_reception_wizard", "=", 1)],
        string="Reason",
    )
    helpdesk_ticket_description = fields.Char(string="Description")

    @api.onchange("helpdesk_ticket_reason_id")
    def _onchange_helpdesk_ticket_reason(self):
        if self.helpdesk_ticket_reason_id:
            if self.helpdesk_ticket_reason_id.location_dest_id:
                self.location_dest_id = self.helpdesk_ticket_reason_id.location_dest_id

    @api.multi
    def _create_helpdesk_ticket(self):
        """Create helpdesk ticket if required."""
        self.ensure_one()
        if self.helpdesk_ticket_reason_id:
            ticket = {
                "helpdesk_ticket_reason_id": self.helpdesk_ticket_reason_id.id,
                "name": self.helpdesk_ticket_description,
                "partner_id": self.partner_id.id,
                "stock_picking_id": self.picking_id.id,
                "product_id": self.operation_id.product_id.id,
                "team_id": self.env.ref("alce_helpdesk.supplier_team").id,
            }
            if self.operation_id.picking_id.purchase_id:
                ticket["purchase_order_id"] = self.picking_id.purchase_id.id
            self.env["helpdesk.ticket"].create(ticket)
        self.helpdesk_ticket_reason_id = False
        self.helpdesk_ticket_description = False

    def _add(self):
        super(StockPackOperationLotAdd, self)._add()
        operation = self.operation_id
        self._create_helpdesk_ticket()
        if self.is_qty_exceeded:
            self.helpdesk_ticket_reason_id = self.env.ref(
                "alce_helpdesk.higher_quantity"
            )
            self.helpdesk_ticket_description = _(
                "Received more than expected qties for product '%s'. (Expected: %d, Received %d)"
            ) % (
                operation.product_id.display_name,
                operation.product_qty,
                operation.qty_done,
            )
            self._create_helpdesk_ticket()
