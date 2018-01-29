# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class ExportSaleOrderTestCase(SavepointCase):

    def setUp(self):
        super(ExportSaleOrderTestCase, self).setUp()

        self.backend_model = self.env['esb.backend']
        self.backend = self.backend_model.get_singleton()

        self.partner = self.env.ref('base.res_partner_1')
        self.prod1 = self.env.ref('product.product_product_1')
        self.prod2 = self.env.ref('product.product_product_2')
        self.setup_records()

    @property
    def model(self):
        return self.env['sale.order']

    def setup_records(self):
        self.delivery = self.env['delivery.carrier'].search(
                [('free_if_more_than', '=', False)], limit=1)
        self.delivery.esb_ref = '03'
        self.prod1.default_code = 'SKU01'
        self.prod1.default_code = 'SKU02'
        self.so1 = self.model.create({
            'esb_ref': 'ref_123',
            'partner_id': self.partner.id,
            'date_order': '2018-01-29',
            'sale_channel': 'fax',
            'carrier_id': self.delivery.id,
            'client_order_ref': 'whatever the client want',
            'delivery_price': 23.5,
            'suite_name': '0123434234',
            'order_line': [
                (0, 0, {
                    'sequence': 1,
                    'name': self.prod1.name,
                    'product_id': self.prod1.id,
                    'product_uom_qty': 7,
                })],
        })

    def test_mapper(self):
        """ Generate data dict with mapper and check with what is expected """
        so = self.so1
        expected = {
            'erp_id': so.id,
            'customer_id': so.partner_id.id,
            'date': so.date_order.split(' ')[0],
            'channel':  '03',  # the code for fax
            'order_ref': so.client_order_ref,
            'status': 'processing',
            'shipping_method': so.carrier_id.esb_ref,
            'apb_tax_amount': 0,
            'order_amount': so.amount_total,
            'tax_amount': int(so.amount_tax),
            'shipping_amount': so.delivery_price,
            'serial_no': int(so.suite_name),
            'increment_id': so.esb_ref,
            'lines': [{
                'line_number': so.order_line[0].sequence,
                'price': so.order_line[0].price_unit,
                'price_inc_tax': (
                    so.order_line[0].price_unit
                    + so.order_line[0].price_reduce_taxinc
                    - so.order_line[0].price_reduce
                    ),
                'qty_ordered': so.order_line[0].product_uom_qty,
                'qty_delivered': so.order_line[0].qty_delivered,
                'qty_cancelled': so.order_line[0].product_qty_canceled,
                'qty_backorder': so.order_line[0].product_qty_unavailable,
                'sku': so.order_line[0].product_id.default_code,
                }]
            }
        with self.backend.work_on(self.model._name) as work:
            mapper = work.component(usage='export.mapper')
            values = mapper.map_record(so).values()
        self.maxDiff = None
        self.assertDictEqual(values, expected)

    def test_correct_postprocess(self):
        """ Test sale order is updated correctely with return values """
        with self.backend.work_on(self.model._name) as work:
            exporter = work.component(usage='record.exporter')
            exporter.record = self.so1
            result = {"erp_id": "42",
                      "increment_id": "1000000348",
                      "lines": [
                         {"line_number": 1, "created_id": 106},
                         ]
                      }
            exporter._postprocess_create_result(result)
        self.assertEqual(self.so1.esb_ref,
                         result['increment_id'])
        self.assertEqual(self.so1.order_line[0].esb_ref,
                         result['lines'][0]['created_id'])
