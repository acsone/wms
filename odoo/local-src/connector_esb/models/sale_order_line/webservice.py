# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import date, datetime
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


class ProductCategoryWebserviceMessage(Component):

    _name = 'esb.webservice.message.product.category'
    _inherit = ['esb.webservice.message.base']
    _apply_on = ['sale.order.line']
    _usage = 'ws.message.customer.stat'

    def _get_base_categories(self):
        """Base categories for sale order line statistics.
        """
        return [
            self.env.ref('specific_data.product_categ_ali'),
            self.env.ref('specific_data.product_categ_medoc'),
            self.env.ref('specific_data.product_categ_materiel'),
        ]

    def _get_all_categories_ids(self, categories):
        """Get list of ids for all child categories of a base categories.
        """
        result = []

        def get_children(category):
            if category.child_id:
                result.extend(category.child_id.ids)
                for child in category.child_id:
                    get_children(child)

        for category in categories:
            result.append(category.id)
            get_children(category)

        return result

    def get_message(self, customer_ref):

        def get_base_category(r):
            """Return the  base category of a sale order line product.
            """
            category = r.product_id.product_tmpl_id.categ_id
            while True:
                if category.parent_id.id == 1:
                    return category.id
                if not category.parent_id:
                    return category.id
                category = category.parent_id

        data = []
        values = {}
        one_year_ago = fields.Date.to_string(
                datetime.today() - relativedelta(years=1))
        two_year_ago = fields.Date.to_string(
                datetime.today() - relativedelta(years=2))
        base_categories = self._get_base_categories()
        all_category_ids = self._get_all_categories_ids(base_categories)

        # Get the sale order line for this customer for the last 2 years
        sol = self.env['sale.order.line'].search(
            [('order_id.partner_id.ref', '=', customer_ref),
             ('order_id.date_order', '>', two_year_ago),
             ('product_id.categ_id.id', 'in', all_category_ids), ])
        # Initialize values structure with the base category required
        for cat in base_categories:
            values.setdefault(cat.id, {
                'productType': cat.alcyon_product_type,
                'purchaseYear': 0,
                'purchaseLastYear': 0,
                })
        for line in sol:
            category_id = get_base_category(line)
            if line.order_id.date_order > one_year_ago:
                values[category_id]['purchaseYear'] += line.price_total
            else:
                values[category_id]['purchaseLastYear'] += line.price_total
        # Format the numeric data properly
        for i, cat in values.iteritems():
            cat['purchaseYear'] = '{0:.2f}'.format(cat['purchaseYear'])
            cat['purchaseLastYear'] = '{0:.2f}'.format(cat['purchaseLastYear'])
            data.append(cat)

        return self._produce_xml(data, list_item_el='resultItem')
