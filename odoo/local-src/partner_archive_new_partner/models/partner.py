# -*- coding: utf-8 -*-
# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    def _get_sale_order_not_done_domain(self):
        return [
            ("state", "!=", "done"),
            "|",
            "|",
            ("partner_id", "=", self.id),
            ("partner_invoice_id", "=", self.id),
            ("partner_shipping_id", "=", self.id),
        ]

    def _get_invoice_unpaid_domain(self):
        return [("state", "!=", "unpaid"), ("partner_id", "=", self.id)]

    def _get_stock_picking_domain(self):
        return [("state", "!=", "done"), ("partner_id", "=", self.id)]

    @api.multi
    def archive_partner(self):
        self.ensure_one()
        if self.active:
            total = 0
            # Check if module `sale` is present
            if "sale.order" in self.env:
                Sale = self.env["sale.order"]
                nb_so_not_done = Sale.search_count(
                    self._get_sale_order_not_done_domain()
                )
                total += nb_so_not_done
            # Check if module `account` is present
            if "account.invoice" in self.env:
                Invoice = self.env["account.invoice"]
                nb_invoices_unpaid = Invoice.search_count(
                    self._get_invoice_unpaid_domain()
                )
                total += nb_invoices_unpaid
            # Check if module `stock` is present
            if "stock.picking" in self.env:
                Picking = self.env["stock.picking"]
                nb_deliveries_not_done = Picking.search_count(
                    self._get_stock_picking_domain()
                )
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
        self.active = not self.active
