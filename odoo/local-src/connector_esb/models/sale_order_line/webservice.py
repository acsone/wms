# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import date
from dateutil.relativedelta import relativedelta
from odoo.addons.component.core import Component
from odoo import fields


class ProductCustomerStatWebserviceMessage(Component):

    _name = 'esb.webservice.message.product.customer.stat'
    _inherit = ['esb.webservice.message.base']
    _apply_on = ['sale.order.line']
    _usage = 'ws.message.product.customer.stat'

    def get_message(self, customer_ref, sku):
        """
            Return a customer monthly purchase statistics for a product during
            the last 12 months. Starting from last month.
        """
        periods = {}
        today = date.today()
        date_start = date(today.year - 1, today.month, 1)
        date_end = date(today.year, today.month, 1)
        # Get the sale order line for the customer and specific product
        # for the last 12 month starting from one month before
        sol = self.env['sale.order.line'].search(
            [('order_id.partner_id.ref', '=', customer_ref),
             ('order_id.date_order', '>=', fields.Date.to_string(date_start)),
             ('order_id.date_order', '<', fields.Date.to_string(date_end)),
             ('product_tmpl_id.default_code', '=', sku)])
        # Compute the statistics for each month
        for m in range(12):
            periods.setdefault(fields.Date.to_string(date_start)[:-3], 0)
            date_start += relativedelta(months=1)
        for line in sol:
            period = line.order_id.date_order[:7]
            periods[period] += line.product_uom_qty
        data = [{'salesPeriod': month, 'salesAverage': '{0:.2f}'.format(qty)}
                for month, qty in periods.iteritems()]
        return self._produce_xml(data)
