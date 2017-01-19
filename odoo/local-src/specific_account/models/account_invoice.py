# -*- coding: utf-8 -*-
# © 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from collections import defaultdict

from openerp import api, fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    supplier_invoice_number = fields.Char('Vendor reference')

    _sql_constraints = [
        ('unique_invoice_number_by_supplier',
         'unique (partner_id,supplier_invoice_number)',
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

    amount_untaxed_with_contribution = fields.Monetary(
        compute='_compute_total_amounts',
    )

    invoice_apb_ids = fields.Many2many('account.invoice.tax',
                                       compute='_compute_total_amounts')
    amount_apb = fields.Monetary(
        compute='_compute_total_amounts'
    )

    invoice_contribution_ids = fields.Many2many(
        'account.invoice.tax',
        compute='_compute_total_amounts')
    amount_contribution = fields.Monetary(
        compute='_compute_total_amounts'
    )

    invoice_only_tax_ids = fields.Many2many(
        'account.invoice.tax',
        compute='_compute_total_amounts')
    amount_only_tax = fields.Monetary(
        compute='_compute_total_amounts'
    )

    amount_untaxed_with_contribution = fields.Monetary(
        compute='_compute_total_amounts',
    )

    @api.depends(
        'invoice_line_ids',
        'invoice_line_ids.quantity',
        'invoice_line_ids.price_unit',
        'invoice_line_ids.price_unit_supplier',
        'invoice_line_ids.price_unit_alcyon',
        'tax_line_ids',
    )
    def _compute_total_amounts(self):
        tax_group_apb = self.env.ref('specific_account.tax_group_apb')

        for inv in self:
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

            amount_apb = amount_contribution = amount_only_tax = 0
            invoice_only_tax_ids = self.env['account.invoice.tax']
            invoice_contribution_ids = self.env['account.invoice.tax']
            invoice_apb_ids = self.env['account.invoice.tax']

            for invoice_tax in inv.tax_line_ids:
                if invoice_tax.tax_id.include_base_amount:
                    invoice_contribution_ids |= invoice_tax
                    amount_contribution += invoice_tax.amount
                elif invoice_tax.tax_id.tax_group_id == tax_group_apb:
                    invoice_apb_ids |= invoice_tax
                    amount_apb += invoice_tax.amount
                else:
                    invoice_only_tax_ids |= invoice_tax
                    amount_only_tax += invoice_tax.amount
            inv.amount_apb = amount_apb
            inv.amount_contribution = amount_contribution
            inv.amount_only_tax = amount_only_tax
            inv.invoice_only_tax_ids = invoice_only_tax_ids
            inv.invoice_contribution_ids = invoice_contribution_ids
            inv.invoice_apb_ids = invoice_apb_ids

            inv.amount_without_discount = sum([
                                          l.price_unit * l.quantity
                                          for l in inv.invoice_line_ids
                                              ]) + amount_contribution

            inv.amount_untaxed_with_contribution = \
                inv.amount_untaxed + amount_contribution

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


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    only_tax_ids = fields.Many2many('account.tax',
                                    compute='_compute_all_taxes')
    contribution_ids = fields.Many2many('account.tax',
                                         compute='_compute_all_taxes')
    apb_ids = fields.Many2many('account.tax', compute='_compute_all_taxes')
    amount_contribution = fields.Monetary(compute='_compute_all_taxes')

    @api.multi
    @api.depends('invoice_line_tax_ids')
    def _compute_all_taxes(self):
        tax_group_apb = self.env.ref('specific_account.tax_group_apb')

        for line in self:
            amount_contribution = 0
            only_tax_ids = self.env['account.tax']
            contribution_ids = self.env['account.tax']
            apb_ids = self.env['account.tax']

            for tax in line.invoice_line_tax_ids:
                if tax.include_base_amount:
                    amount_contribution += (tax.amount * line.quantity)
                    contribution_ids |= tax
                elif tax.tax_group_id == tax_group_apb:
                    apb_ids |= tax
                else:
                    only_tax_ids |= tax

            line.only_tax_ids = only_tax_ids
            line.contribution_ids = contribution_ids
            line.apb_ids = apb_ids
            line.amount_contribution = amount_contribution
