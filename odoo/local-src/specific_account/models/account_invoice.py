# -*- coding: utf-8 -*-
# © 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from collections import defaultdict

from openerp import api, fields, models, _
from openerp.exceptions import Warning


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

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

    @api.multi
    def get_instrastat_values(self):
        values_by_intrastat = {}

        for line in self.invoice_line_ids:
            if not line.product_id or not line.product_id.intrastat_id:
                continue
            intrastat = line.product_id.intrastat_id

            weight = line.product_id.weight * line.quantity
            amount = line.price_subtotal

            intrastat_value = values_by_intrastat.get(intrastat.name, [])
            if not intrastat_value:
                intrastat_value = [weight, amount]
            else:
                total_weight = intrastat_value[0] + weight
                total_amount = intrastat_value[1] + amount
                intrastat_value = [total_weight, total_amount]

            values_by_intrastat[intrastat.name] = intrastat_value

        values = [(code, value[0], value[1])
                  for code, value in values_by_intrastat.iteritems()]
        values.sort(key=lambda line: line[0])

        return values
