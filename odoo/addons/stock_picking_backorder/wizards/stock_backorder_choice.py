# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

from odoo import fields, models


class StockBackorderChoice(models.TransientModel):
    _name = "stock.backorder.choice"

    picking_id = fields.Many2one(
        comodel_name="stock.picking",
        string="Picking",
        readonly=True,
        ondelete="cascade",
    )
    reason_id = fields.Many2one(
        comodel_name="stock.backorder.reason",
        string="Backorder reason",
        required=True,
        ondelete="cascade",
    )
    backorder_action_to_do = fields.Selection(
        related="reason_id.backorder_action_to_do", readonly=True
    )
    is_purchase_back_order_accepted = fields.Boolean(
        related="picking_id.partner_id.is_purchase_back_order_accepted", readonly=True
    )
    is_helpdesk_ticket_to_create = fields.Boolean(
        related="reason_id.is_helpdesk_ticket_to_create", readonly=True
    )
    helpdesk_ticket_reason_id = fields.Many2one(
        related="reason_id.helpdesk_ticket_reason_id", readonly=True, ondelete="cascade"
    )
    helpdesk_ticket_description = fields.Char(string="Helpdesk ticket description")

    def _get_helpdesk_ticket_values(self):
        po = self.env["purchase.order"].search(
            [("name", "=", self.picking_id.origin)], limit=1
        )
        return {
            "description": self.helpdesk_ticket_description,
            "helpdesk_ticket_reason_id": self.helpdesk_ticket_reason_id.id,
            "stock_picking_id": self.picking_id.id,
            "partner_id": self.picking_id.partner_id.id,
            "purchase_order_id": po and po.id or False,
        }

    def apply(self):
        self.ensure_one()
        if self.is_helpdesk_ticket_to_create:
            self.env["helpdesk.ticket"].create(self._get_helpdesk_ticket_values())
        keep_backorder = self.backorder_action_to_do == "create" or (
            self.backorder_action_to_do == "use_partner_option"
            and self.picking_id.partner_id.is_purchase_back_order_accepted
        )
        backorder_wiz = self.env["stock.backorder.confirmation"].create(
            {"pick_id": self.picking_id.id}
        )
        if keep_backorder:
            backorder_wiz.process()
            if self.reason_id.keep_grn:
                backorder = self.env["stock.picking"].search(
                    [("backorder_id", "=", self.picking_id.id)]
                )
                backorder.grn_id = self.picking_id.grn_id
        else:
            backorder_wiz.process_cancel_backorder()
