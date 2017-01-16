# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Sylvain Van Hoof <svh@sylvainvh.be>
#    Copyright 2016 BCIM sprl, Camptocamp
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from collections import defaultdict

from openerp import models, fields, api


class StockMove(models.Model):
    _inherit = 'stock.move'

    order_line_id = fields.Many2one('sale.order.line',
                                    string='Order line',
                                    related='procurement_id.sale_line_id',
                                    store=True)
    order_id = fields.Many2one('sale.order', related='order_line_id.order_id')


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def get_total_amounts(self):
        tax_group_apb = self.env.ref('specific_account.tax_group_apb')

        for picking in self:
            amount_without_discount = 0
            amount_supplier_discount = 0
            amount_alcyon_discount = 0
            amount_untaxed = 0
            amount_apb = 0
            amount_vat = 0
            amount_total = 0

            for line in picking.move_lines:
                if not line.order_line_id:
                    continue
                sol = line.order_line_id

                amount_without_discount += \
                    (sol.unit_price * sol.qty_delivered)
                amount_supplier_discount += \
                    (sol.price_unit - sol.price_unit_supplier) * sol.qty_delivered
                amount_alcyon_discount += \
                    (sol.price_unit - sol.price_unit_alcyon) * sol.qty_delivered
                amount_untaxed += sol.price_subtotal

                price = sol.price_unit * (1 - (sol.discount or 0.0) / 100.0)

                if sol.edited_supplier_promotion or sol.edited_alcyon_discount:
                    price_supplier, price_alcyon = sol._compute_discount_prices(
                        price
                    )
                else:
                    price_supplier, price_alcyon = sol._compute_pricelist_prices(
                        price
                    )
                taxes = line.tax_id.compute_all(
                    price_alcyon, line.order_id.currency_id,
                    line.product_uom_qty,
                    product=line.product_id, partner=line.order_id.partner_id
                )

            # for invoice_tax in inv.tax_line_ids:
            #     if invoice_tax.tax_id.include_base_amount:
            #         invoice_contribution_ids |= invoice_tax
            #         amount_contribution += invoice_tax.amount
            #     elif invoice_tax.tax_id.tax_group_id == tax_group_apb:
            #         invoice_apb_ids |= invoice_tax
            #         amount_apb += invoice_tax.amount
            #     else:
            #         invoice_only_tax_ids |= invoice_tax
            #         amount_only_tax += invoice_tax.amount
            # inv.amount_apb = amount_apb
            # inv.amount_contribution = amount_contribution
            # inv.amount_only_tax = amount_only_tax
            # inv.invoice_only_tax_ids = invoice_only_tax_ids
            # inv.invoice_contribution_ids = invoice_contribution_ids
            # inv.invoice_apb_ids = invoice_apb_ids
            #
            # inv.amount_without_discount = sum([
            #                                       l.price_unit * l.quantity
            #                                       for l in inv.invoice_line_ids
            #                                       ]) + amount_contribution
            #
            # inv.amount_untaxed_with_contribution = \
            #     inv.amount_untaxed + amount_contribution

        return []

    @api.multi
    def get_moves_by_order(self):
        self.ensure_one()

        moves_by_order = defaultdict(list)
        backorder_moves_by_order = defaultdict(list)
        result = []
        moves_witout_order = []
        backorder_moves_without_order = []
        for line in self.move_lines_related:
            if not line.order_id:
                moves_witout_order.append(line)
            else:
                moves_by_order[line.order_id].append(line)

        backorders = self.env['stock.picking']. \
            search([('backorder_id', '=', self.id)])
        for backorder in backorders:
            for line in backorder.move_lines_related:
                if not line.order_id:
                    backorder_moves_without_order.append(line)
                else:
                    backorder_moves_by_order[line.order_id].append(line)

        result_dict = {}
        for order, moves in moves_by_order.iteritems():
            result_dict[order] = [moves, backorder_moves_by_order.get(order, [])]

        if moves_witout_order:
            result.append((None, moves_witout_order, backorder_moves_without_order))

        result.extend(
            sorted(result_dict.items(),
                   key=lambda picking: (picking[0][0].date_order, picking[0][0].id))
        )
        return result
