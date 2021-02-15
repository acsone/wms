# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

from odoo import _, fields, models


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

    def apply(self):
        self.ensure_one()

        picking = self.env["stock.picking"].search([("id", "=", self.picking_id.id)])
        picking.message_post(
            body=_("Back order reason: <em>%s</em>.") % (self.reason_id.name)
        )
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
