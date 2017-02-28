# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.addons.decimal_precision import decimal_precision as dp


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def get_taxes_values(self):
        """ Have to copied this method from account.invoice because
        Odoo does not base his tax computation on subtotal but on price_unit
        (and recompute price_unit * discount.....)
        """
        tax_grouped = {}
        for line in self.invoice_line_ids:
            taxes = line.invoice_line_tax_ids.compute_all(
                line.price_unit_alcyon, self.currency_id, line.quantity,
                line.product_id, self.partner_id
            )['taxes']
            for tax in taxes:
                val = self._get_tax_val(line, tax)
                key = tax['id']
                if key not in tax_grouped:
                    tax_grouped[key] = val
                else:
                    tax_grouped[key]['amount'] += val['amount']
        return tax_grouped

    def _get_tax_val(self, line, tax):
        """ Extract part of "get_taxes_values" copied method.
        """
        val = {
            'invoice_id': self.id,
            'name': tax['name'],
            'tax_id': tax['id'],
            'amount': tax['amount'],
            'manual': False,
            'sequence': tax['sequence'],
            'account_analytic_id':
                tax['analytic'] and line.account_analytic_id.id or False,
            'account_id':
                self.type in ('out_invoice', 'in_invoice') and (
                    tax['account_id'] or line.account_id.id
                ) or (
                    tax['refund_account_id'] or line.account_id.id
                ),
        }

        # If the taxes generate moves on the same
        # financial account as the invoice line,
        # propagate the analytic account from the invoice line to the tax line.
        # This is necessary in situations were (part of)
        # the taxes cannot be reclaimed,
        # to ensure the tax move is allocated to the proper analytic account.
        if not val.get('account_analytic_id') \
                and line.account_analytic_id \
                and val['account_id'] == line.account_id.id:
            val['account_analytic_id'] = line.account_analytic_id.id

        return val


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    price_unit_supplier = fields.Monetary(
        compute='_compute_price_unit_discount',
    )

    price_unit_alcyon = fields.Monetary(
        compute='_compute_price_unit_discount',
    )

    supplier_promotion = fields.Float(
        string='Promotion (%)',
        digits_compute=dp.get_precision('Discount')
    )
    alcyon_discount = fields.Float(
        string='Discount (%)',
        digits_compute=dp.get_precision('Discount')
    )

    @api.depends('price_unit', 'supplier_promotion', 'alcyon_discount')
    def _compute_price_unit_discount(self):
        """ Recompute supplier and alcyon price based on unit price and
        discount percentages.
        """
        for line in self:
            currency_round = line.invoice_id.currency_id.round
            if not line.price_unit:
                supplier_price = 0.0
                alcyon_price = 0.0
            else:
                supplier_price = currency_round(line.price_unit * (
                    1 - (line.supplier_promotion or 0.0) / 100.0
                ))
                alcyon_price = (supplier_price * (
                    1 - (line.alcyon_discount or 0.0) / 100.0
                ))
            line.update({
                'price_unit_supplier': supplier_price,
                'price_unit_alcyon': alcyon_price,
            })

    @api.depends(
        'invoice_line_tax_ids', 'quantity',
        'product_id', 'invoice_id.partner_id', 'invoice_id.currency_id',
        'invoice_id.company_id', 'price_unit_alcyon'
    )
    def _compute_price(self):
        """ Override account.invoice prices computation to be based
        on price_unit_alcyon which contains supplier and alcyon discount.
        """
        for line in self:
            currency = line.invoice_id and line.invoice_id.currency_id or None
            taxes = False
            if line.invoice_line_tax_ids:
                taxes = line.invoice_line_tax_ids.compute_all(
                    line.price_unit_alcyon, currency, line.quantity,
                    product=line.product_id, partner=line.invoice_id.partner_id
                )
            line.price_subtotal = price_subtotal_signed = (
                taxes['total_excluded']
                if taxes else line.quantity * line.price_unit_alcyon
            )

            if currency and currency != line.invoice_id.company_id.currency_id:
                price_subtotal_signed = currency.compute(
                    price_subtotal_signed,
                    line.invoice_id.company_id.currency_id
                )

            sign = \
                line.invoice_id.type in ['in_refund', 'out_refund'] and -1 or 1
            line.price_subtotal_signed = price_subtotal_signed * sign
