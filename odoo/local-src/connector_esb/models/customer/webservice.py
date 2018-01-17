# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from collections import namedtuple
from itertools import groupby

from odoo import fields
from odoo.addons.component.core import Component


StatsFormOptions = namedtuple(
    'StatsFormOptions',
    'customer_ref start end product_type suppliers language'
)
# Make None the default value for fields
# customer_ref is required, hence the len(fields) - 1
StatsFormOptions.__new__.__defaults__ = (
    (None,) * (len(StatsFormOptions._fields) - 1)
)


class StatisticsFormWebserviceMessage(Component):

    _name = 'esb.webservice.message.statistics.form'
    _inherit = ['esb.webservice.message.base']
    _apply_on = ['res.partner']
    _usage = 'ws.message.statistics.form'

    options_for_form = StatsFormOptions

    def _data_for_message(self, options):
        partner = self.env['res.partner'].search(
            [('ref', '=', options.customer_ref)],
            limit=1,
        )
        partner_and_addresses = self.env['res.partner'].search(
            [('parent_id', 'child_of', partner.id)],
        )

        domain = [('order_id.partner_id', 'in', partner_and_addresses.ids),
                  ('invoice_status', '=', 'invoiced')]
        if options.start:
            domain_start = fields.Date.to_string(options.start)
            domain.append(('order_id.date_order', '>=', domain_start))
        if options.end:
            domain_end = fields.Date.to_string(options.end)
            domain.append(('order_id.date_order', '<=', domain_end))
        if options.product_type:
            domain.append(
                ('product_id.categ_id.alcyon_product_type', '=',
                 options.product_type)
            )
        if options.suppliers:
            domain.append(
                ('product_id.seller_ids.name.ref', 'in', options.suppliers)
            )

        lang_code = options.language or 'FR'
        lang = self.env['res.lang'].search([('esb_ref', '=', lang_code)])

        line_model = self.env['sale.order.line'].with_context(lang=lang.code)
        lines = line_model.search(domain)

        data = []
        lines = lines.sorted(lambda l: l.product_id.id)
        for __, lines in groupby(lines, key=lambda l: l.product_id.id):
            lines = list(lines)
            delivered = 0.
            total = 0.
            for line in lines:
                delivered += line.qty_delivered
                # compute total price only for delivered items
                price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                taxes = line.tax_id.compute_all(
                    price, line.order_id.currency_id, delivered,
                    product=line.product_id,
                    partner=line.order_id.partner_shipping_id
                )
                total += taxes['total_excluded']

            product = lines[0].product_id
            rate = lines[0].tax_id.amount if lines[0].tax_id else 0.0
            supplier = (','.join(product.mapped('seller_ids.name.ref'))
                        if product.seller_ids else '')
            values = {
                'sku': product.default_code,
                'productName': product.name,
                'productType': product.categ_id.alcyon_product_type,
                'manufacturer': supplier,
                'qtyDelivered': delivered,
                'totalPrice': round(total, 3),
                'taxRate': rate,
            }
            data.append(values)
        return data

    def get_message(self, options):
        return self._produce_xml(self._data_for_message(options))
