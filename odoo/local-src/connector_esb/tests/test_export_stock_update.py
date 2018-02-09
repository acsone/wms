# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta
from odoo.tests.common import SavepointCase


class ExportStockUpdateTestCase(SavepointCase):

    def setUp(self):
        super(ExportStockUpdateTestCase, self).setUp()
        self.backend_model = self.env['esb.backend']
        self.backend = self.backend_model.get_singleton()
        self.setup_records()
        self.maxDiff = None
        self.timestamp = self.env.ref(
                'connector_esb.esb_timestamp_stock_update')

    @property
    def model(self):
        return self.env['product.product']

    def setup_records(self):
        self.partner = self.env.ref('base.res_partner_1')
        self.location = self.env.ref('stock.stock_location_stock').id
        self.prod1 = self.env.ref('product.product_product_1')
        self.prod1.default_code = 'ref1'
        self.prod1.state_id = self.env.ref('specific_purchase.product_state_a')
        self.prod2 = self.env.ref('product.product_product_2')
        self.prod2.default_code = 'ref2'

        # Keep only one sale order line with a quantity for product 1 so
        # we can test the sale_average on the mapper
        one_year_back = (datetime.today() - timedelta(days=365))
        sol = self.env['sale.order.line'].search([
            ('product_id', '=', self.prod1.id),
            ('create_date', '>', one_year_back.strftime("%Y-%m-%d"))])
        sol.write({'product_uom_qty': 0})
        sol[0].write({'product_uom_qty': 55})
        # And add a canceled sale order that should not be part of the
        # sales_average computation
        self.so1 = self.env['sale.order'].create({
            'esb_ref': 'ref_123',
            'partner_id': self.partner.id,
            'sale_channel': 'fax',
            'client_order_ref': 'whatever the client want',
            'delivery_price': 23.5,
            'suite_name': '0123434234',
            'state': 'cancel',
            'order_line': [
                (0, 0, {
                    'sequence': 1,
                    'name': 'prod 1',
                    'product_id': self.prod1.id,
                    'product_uom_qty': 7,
                })],
        })

        # Lets add some stock
        self.use_date_1 = datetime.today() + timedelta(weeks=40)
        self.use_date_2 = datetime.today() + timedelta(weeks=1)
        self.use_date_3 = datetime.today() + timedelta(days=1)
        self.lot1 = self.env['stock.production.lot'].create({
            'product_id': self.prod1.id,
            'name': 'lot1',
            'use_date': self.use_date_1.strftime("%Y-%m-%d %H:%M:%S")
            })
        self.lot2 = self.env['stock.production.lot'].create({
            'product_id': self.prod1.id,
            'name': 'lot2',
            'use_date': self.use_date_2.strftime("%Y-%m-%d %H:%M:%S")
            })
        inventory_wizard = self.env['stock.change.product.qty'].create({
            'product_id': self.prod1.id,
            'new_quantity': 50.0,
            'location_id': self.location,
            'lot_id': self.lot2.id
        })
        inventory_wizard.change_product_qty()
        inventory_wizard = self.env['stock.change.product.qty'].create({
            'product_id': self.prod1.id,
            'new_quantity': 25.0,
            'location_id': self.location,
            'lot_id': self.lot1.id
        })
        inventory_wizard.change_product_qty()
        # Add another product to see that it does not interfere
        self.lot_p2 = self.env['stock.production.lot'].create({
            'product_id': self.prod2.id,
            'name': 'lot_p2',
            'use_date': self.use_date_3.strftime("%Y-%m-%d %H:%M:%S")
            })
        inventory_wizard = self.env['stock.change.product.qty'].create({
            'product_id': self.prod2.id,
            'new_quantity': 25.0,
            'location_id': self.location,
            'lot_id': self.lot_p2.id
        })
        inventory_wizard.change_product_qty()

    def test_mapper(self):
        """ Generate data dict with mapper and check with what is expected """
        product = self.prod1
        expected = {'sku': u'ref1',
                    'qty': 50 + 25,
                    'sales_average': '{0:.3f}'.format(55.0/365),
                    'erp_stock_code': u'A',
                    'date_peremption': self.use_date_2.strftime("%Y-%m-%d"),
                    }
        with self.backend.work_on(self.model._name,
                                  timestamp=self.timestamp) as work:
            mapper = work.component(usage='export.mapper')
            values = mapper.map_record(product).values()
        self.assertDictEqual(values, expected)
