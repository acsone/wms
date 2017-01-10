# -*- coding: utf-8 -*-
# © 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from collections import defaultdict

from openerp import api, fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    supplier_invoice_number = fields.Char('Vendor reference')

    _sql_constraints = [
        ('unique_invoice_number_by_supplier', 'unique (partner_id,supplier_invoice_number)',
         'The supplier invoice number must be unique by supplier')
    ]

    amount_without_discount = fields.Monetary(
        compute='_compute_total_amounts',
    )

    amount_supplier_discount = fields.Monetary(
        compute='_compute_total_amounts',
    )

    amount_alcyon_discount = fields.Monetary(
        compute='_compute_total_amounts',
    )

    amount_discount_total = fields.Monetary(
        compute='_compute_total_amounts',
    )

    @api.depends(
        'invoice_line_ids',
        'invoice_line_ids.quantity',
        'invoice_line_ids.price_unit',
        'invoice_line_ids.price_unit_supplier',
        'invoice_line_ids.price_unit_alcyon',
    )
    def _compute_total_amounts(self):
        for inv in self:
            inv.amount_without_discount = sum([
                l.price_unit * l.quantity
                for l in inv.invoice_line_ids
            ])

            inv.amount_supplier_discount = sum([
                (l.price_unit - l.price_unit_supplier) * l.quantity
                for l in inv.invoice_line_ids
            ])

            inv.amount_alcyon_discount = sum([
                (l.price_unit_supplier - l.price_unit_alcyon) * l.quantity
                for l in inv.invoice_line_ids
            ])

            inv.amount_discount_total = (
                inv.amount_supplier_discount + inv.amount_alcyon_discount
            )

    @api.multi
    def get_lines_by_sale(self):
        self.ensure_one()

        result = []
        sales = defaultdict(list)
        orphans = []
        for line in self.invoice_line_ids:
            order = line.sale_line_ids.mapped('order_id')
            if not order:
                orphans.append(line)

            elif len(order) > 1:
                raise ValueError("Multiple sale order for one invoice line.")

            else:
                sales[order].append(line)

        if orphans:
            result.append((None, orphans))

        result.extend(
            sorted(sales.items(), key=lambda x: (x[0].date_order, x[0].id))
        )
        return result
