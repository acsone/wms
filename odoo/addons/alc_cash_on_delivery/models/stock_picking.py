# Copyright 2018 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields

from odoo.addons.account.models.account_move import AccountMove
from odoo.addons.stock.models.stock_picking import Picking


class StockPicking(Picking):
    cash_on_delivery_invoice_ids = fields.Many2many[AccountMove](
        string="Invoice", copy=False, readonly=True
    )

    def button_validate(self):
        res = super().button_validate()
        for rec in self:
            sales = rec.move_ids.filtered(
                lambda move: move.state == "done"
                and not move.location_dest_id.scrap_location
                and move.location_dest_id.usage == "customer"
            ).mapped("sale_line_id.order_id")
            cash_on_delivery_sales = sales.filtered(
                lambda sale: sale.payment_term_id.cash_on_delivery
            )
            if cash_on_delivery_sales:
                invoice_ids = cash_on_delivery_sales._create_invoices(final=True)
                if invoice_ids:
                    # invoices = self.env["account.move"].browse(invoice_ids)
                    # Validate invoices
                    invoice_ids.action_post()
                    rec.cash_on_delivery_invoice_ids = [(6, 0, invoice_ids.ids)]
        return res
