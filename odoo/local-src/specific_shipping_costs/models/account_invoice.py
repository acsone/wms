# -*- coding: utf-8 -*-
# Copyright 2017 Julien Coux (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tools import float_compare

from odoo import models, fields, api, _


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    shipping_costs_computed = fields.Boolean()

    allow_compute_shipping_costs = fields.Boolean(
        compute='_compute_allow_compute_shipping_costs',
    )

    @api.depends('invoice_line_ids')
    def _compute_allow_compute_shipping_costs(self):
        for invoice in self:
            if invoice.type == 'out_invoice':
                deliveries_carrier = invoice.invoice_line_ids.mapped(
                    'sale_line_ids.order_id.carrier_id'
                ).filtered(
                    lambda d: d.compute_shipping_costs_on_invoice
                )
                invoice.allow_compute_shipping_costs = (
                    len(deliveries_carrier) > 0
                )
            else:
                invoice.allow_compute_shipping_costs = False

    @api.multi
    def compute_shipping_costs(self):
        precision = self.env['decimal.precision'].precision_get('Account')
        for invoice in self:
            invoice.invoice_line_ids.filtered(
                lambda l: l.is_shipping_line
            ).unlink()

            deliveries_carrier = invoice.invoice_line_ids.mapped(
                'sale_line_ids.order_id.carrier_id'
            ).filtered(
                lambda d: d.compute_shipping_costs_on_invoice
            )

            lines = []
            for delivery_carrier in deliveries_carrier:
                invoice_lines = (
                    invoice.invoice_line_ids.filtered(
                        lambda l: delivery_carrier.id in l.mapped(
                            'sale_line_ids.order_id.carrier_id'
                        ).ids
                    )
                )

                round_instances = invoice_lines.mapped(
                    'move_line_ids.picking_id.delivery_round_id'
                )

                for round_instance in round_instances:

                    round_invoice_lines = (
                        invoice_lines.filtered(
                            lambda l: round_instance in l.mapped(
                                'move_line_ids.picking_id.delivery_round_id'
                            )
                        )
                    )

                    invoice_lines_amount = sum([
                        line.price_subtotal
                        for line in round_invoice_lines
                    ])

                    # invoice_lines_amount < delivery_carrier.amount
                    if float_compare(
                            invoice_lines_amount,
                            delivery_carrier.amount,
                            precision_digits=precision
                    ) == -1:
                        account = self.env[
                            'account.invoice.line'
                        ].get_invoice_line_account(
                            type=invoice.type,
                            product=delivery_carrier.product_id,
                            fpos=invoice.fiscal_position_id,
                            company=invoice.company_id,
                        )
                        lines.append(
                            (0, 0, {
                                'product_id': delivery_carrier.product_id.id,
                                'price_unit': (
                                    delivery_carrier.product_id.list_price
                                ),
                                'account_id': account.id,
                                'name': '%s - %s' % (
                                    delivery_carrier.product_id.name,
                                    round_instance.name
                                ),
                                'is_shipping_line': True,
                            })
                        )
            values = {
                'shipping_costs_computed': True,
            }
            if lines:
                values['invoice_line_ids'] = lines
            invoice.update(values)

    @api.multi
    def write(self, vals):
        if vals.get('state') and vals['state'] in ['open', 'paid']:
            for invoice in self:
                shipping_costs_computed_required = (
                    invoice.allow_compute_shipping_costs
                    and not invoice.shipping_costs_computed
                )
                if shipping_costs_computed_required:
                    raise ValidationError(
                        _("An invoice can't be opened or paid "
                          "if shipping costs are not computed")
                    )
        return super(AccountInvoice, self).write(vals)


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    is_shipping_line = fields.Boolean()
