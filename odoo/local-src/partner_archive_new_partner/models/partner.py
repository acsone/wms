# -*- coding: utf-8 -*-
# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    def _get_sale_order_not_done_domain(self):
        return [
            ("state", "not in", ["done", "cancel"]),
            "|",
            "|",
            ("partner_id", "=", self.id),
            ("partner_invoice_id", "=", self.id),
            ("partner_shipping_id", "=", self.id),
        ]

    def _get_invoice_unpaid_domain(self):
        return [
            ("state", "not in", ["paid", "cancel"]),
            ("partner_id", "=", self.id),
        ]

    def _get_stock_picking_domain(self):
        return [
            ("state", "not in", ["done", "cancel"]),
            ("partner_id", "=", self.id),
        ]

    @api.multi
    def archive_partner(self):
        self.ensure_one()
        if self.active:
            context = {}
            Sale = self.env["sale.order"]
            nb_so_not_done = Sale.search(
                self._get_sale_order_not_done_domain()
            )
            if nb_so_not_done:
                context["default_sale_ids"] = nb_so_not_done.ids
            Invoice = self.env["account.invoice"]
            nb_invoices_unpaid = Invoice.search(
                self._get_invoice_unpaid_domain()
            )
            if nb_so_not_done:
                context["default_invoice_ids"] = nb_invoices_unpaid.ids

            Picking = self.env["stock.picking"]
            nb_deliveries_not_done = Picking.search(
                self._get_stock_picking_domain()
            )
            if nb_so_not_done:
                context["default_picking_ids"] = nb_deliveries_not_done.ids
            if context:
                context["default_old_partner_id"] = self.id
                return {
                    "name": "Select new partner before archiving",
                    "type": "ir.actions.act_window",
                    "view_type": "form",
                    "view_mode": "form",
                    "res_model": "partner.archive.new.partner.wizard",
                    "context": context,
                    "target": "new",
                }
        self.active = not self.active
