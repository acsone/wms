# -*- coding: utf-8 -*-
# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class PartnerArchiveWizard(models.TransientModel):
    _name = "partner.archive.new.partner.wizard"

    old_partner_id = fields.Many2one(comodel_name="res.partner")
    new_partner_id = fields.Many2one(
        comodel_name="res.partner", string="New partner", required="True"
    )

    def action_confirm(self):
        """Search for objects to realocate

        It supports sales, account and stock modules.
        Which are not dependencies.
        """
        # Check if module `sale` is present
        if "sale.order" in self.env:
            so_not_done = self.env["sale.order"].search(
                [
                    ("state", "!=", "done"),
                    "|",
                    "|",
                    ("partner_id", "=", self.old_partner_id.id),
                    ("partner_invoice_id", "=", self.old_partner_id.id),
                    ("partner_shipping_id", "=", self.old_partner_id.id),
                ]
            )
            for so in so_not_done:
                if so.partner_id.id == self.old_partner_id.id:
                    so.write({"partner_id": self.new_partner_id.id})
                if so.partner_shipping_id.id == self.old_partner_id.id:
                    so.write({"partner_shipping_id": self.new_partner_id.id})
                if so.partner_invoice_id.id == self.old_partner_id.id:
                    so.write({"partner_invoice_id": self.new_partner_id.id})

        # Check if module `account` is present
        if "account.invoice" in self.env:
            invoices_unpaid = self.env["account.invoice"].search(
                [
                    ("state", "!=", "unpaid"),
                    ("partner_id", "=", self.old_partner_id.id),
                ]
            )
            invoices_unpaid.write({"partner_id": self.new_partner_id.id})

        # Check if module `stock` is present
        if "stock.picking" in self.env:
            deliveries_not_done = self.env["stock.picking"].search(
                [
                    ("state", "!=", "done"),
                    ("partner_id", "=", self.old_partner_id.id),
                ]
            )
            deliveries_not_done.write({"partner_id": self.new_partner_id.id})

        self.env["res.partner"].browse(self.env.context["active_id"]).write(
            {"active": False}
        )
