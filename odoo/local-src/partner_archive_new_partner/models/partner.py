# -*- coding: utf-8 -*-
# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.multi
    def archive_partner(self):
        for rec in self:
            if rec.active:
                total = 0
                if "sale.order" in self.env:
                    nb_so_not_done = self.env["sale.order"].search_count([
                        ("state", "!=", "done"),
                        "|", "|",
                        ("partner_id", "=", rec.id),
                        ("partner_invoice_id", "=", rec.id),
                        ("partner_shipping_id", "=", rec.id),
                    ])
                    total += nb_so_not_done
                if "account.invoice" in self.env:
                    nb_invoices_unpaid = self.env["account.invoice"].search_count([
                        ("state", "!=", "unpaid"),
                        ("partner_id", "=", rec.id),
                    ])
                    total += nb_invoices_unpaid
                if "stock.picking" in self.env:
                    nb_deliveries_not_done = self.env["stock.picking"].search_count([
                        ("state", "!=", "done"),
                        ("partner_id", "=", rec.id),
                    ])
                    total += nb_deliveries_not_done
                if total > 0:
                    return {
                        "name": "Select new partner before archiving",
                        "type": "ir.actions.act_window", 
                        "view_type": "form", 
                        "view_mode": "form",
                        "res_model": "partner.archive.new.partner.wizard", 
                        "context": {"default_old_partner_id": self.id},
                        "target": "new", 
                    }
            rec.active = not rec.active
