# -*- coding: utf-8 -*-
# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class PartnerArchiveWizard(models.TransientModel):
    _name = "partner.archive.new.partner.wizard"

    old_partner_id = fields.Many2one(comodel_name="res.partner")
    old_partner_company_id = fields.Many2one(related="old_partner_id.company_id")
    new_partner_id = fields.Many2one(
        comodel_name="res.partner", string="New partner", required="True"
    )
    sale_ids = fields.Many2many("sale.order", string="Sale orders", readonly=True)
    picking_ids = fields.Many2many("stock.picking", string="Pickings", readonly=True)
    invoice_ids = fields.Many2many("account.invoice", string="Invoices", readonly=True)

    def action_confirm(self):
        """Search for objects to reallocate"""

        so_not_done = self.env["sale.order"].search(
            self.old_partner_id._get_sale_order_not_done_domain()
        )
        for so in so_not_done:
            if so.partner_id == self.old_partner_id:
                so.write({"partner_id": self.new_partner_id.id})
            if so.partner_shipping_id == self.old_partner_id:
                so.write({"partner_shipping_id": self.new_partner_id.id})
            if so.partner_invoice_id == self.old_partner_id:
                so.write({"partner_invoice_id": self.new_partner_id.id})

        invoices_unpaid = self.env["account.invoice"].search(
            self.old_partner_id._get_invoice_unpaid_domain()
        )
        invoices_unpaid.write({"partner_id": self.new_partner_id.id})

        deliveries_not_done = self.env["stock.picking"].search(
            self.old_partner_id._get_stock_picking_domain()
        )
        deliveries_not_done.write({"partner_id": self.new_partner_id.id})

        self.env["res.partner"].browse(self.env.context["active_id"]).write(
            {"active": False}
        )
