# -*- coding: utf-8 -*-
# Copyright 2018 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    cash_on_delivery_invoice_ids = fields.Many2many(
        'account.invoice', string='Invoice', copy=False, readonly=True
    )

    def do_transfer(self):
        res = super(StockPicking, self).do_transfer()
        for rec in self:
            sales = rec.move_lines.filtered(
                lambda move: move.state == 'done'
                and not move.location_dest_id.scrap_location
                and move.location_dest_id.usage == 'customer'
            ).mapped('procurement_id.sale_line_id.order_id')
            cash_on_delivery_sales = sales.filtered(
                lambda sale: sale.payment_term_id.cash_on_delivery
            )
            if cash_on_delivery_sales:
                invoice_ids = cash_on_delivery_sales.action_invoice_create(
                    final=True
                )
                if invoice_ids:
                    invoices = self.env['account.invoice'].browse(invoice_ids)
                    # Validate invoices
                    invoices.action_invoice_open()
                    rec.cash_on_delivery_invoice_ids = [(6, 0, invoices.ids)]
        return res
