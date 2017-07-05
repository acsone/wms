# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta
from odoo import tools, fields
from .common import ESBXMLTestCase


class ExportStockTestCase(ESBXMLTestCase):

    def setUp(self):
        super(ExportStockTestCase, self).setUp()
        self.setup_records()
        self.maxDiff = None
        self.timestamp = self.env.ref('connector_esb.esb_timestamp_stock')

    @property
    def model(self):
        return self.env['product.product']

    def setup_records(self):
        # Use an existing product
        self.product_18 = self.env.ref('product.product_product_8')
        # Set existing quants to a very old date so they don't interfere
        self.env.cr.execute("update stock_quant set write_date='1900-01-01'")
        # Add a warehouses
        self.warehouse_1 = self.env['stock.warehouse'].create({
            'name': 'First Warehouses',
            'reception_steps': 'one_step',
            'delivery_steps': 'ship_only',
            'code': 'W1'})
        # With a location
        self.location_1 = self.env['stock.location'].create({
            'name': 'TestLocation1',
            'posx': 3,
            'location_id': self.warehouse_1.lot_stock_id.id,
        })
        # Add some products in the stock
        # From different lots with different expirity date
        self.use_date_1 = datetime.today() + timedelta(weeks=40)
        self.use_date_2 = datetime.today() + timedelta(weeks=1)
        self.lot1 = self.env['stock.production.lot'].create({
            'product_id': self.product_18.id,
            'name': 'lot1',
            'use_date': self.use_date_1.strftime("%Y-%m-%d %H:%M:%S")
            })
        self.lot2 = self.env['stock.production.lot'].create({
            'product_id': self.product_18.id,
            'name': 'lot2',
            'use_date': self.use_date_2.strftime("%Y-%m-%d %H:%M:%S")
            })
        inventory_wizard = self.env['stock.change.product.qty'].create({
            'product_id': self.product_18.id,
            'new_quantity': 50.0,
            'location_id': self.warehouse_1.lot_stock_id.id,
            'lot_id': self.lot2.id
        })
        inventory_wizard.change_product_qty()
        inventory_wizard = self.env['stock.change.product.qty'].create({
            'product_id': self.product_18.id,
            'new_quantity': 25.0,
            'location_id': self.warehouse_1.lot_stock_id.id,
            'lot_id': self.lot1.id
        })
        inventory_wizard.change_product_qty()
        # Set one of the quant to an older date
        quant = self.env['stock.quant'].search([
            ('product_id', '=', self.product_18.id),
            ('qty', '=', 50.0)])
        quant[0].write_date = datetime(1984, 1, 1).strftime(
                "%Y-%m-%d %H:%M:%S")

    def test_mapper(self):
        """ Generate dict with the mapper and compare with what is expected"""
        expected = {
            'Sku': 'E-COM09',
            'Stock': 75.0,
            'NextUseDate': self.use_date_2.strftime("%Y-%m-%d"),
            # 'SalesAverage': '',
            'ErpStockCode': '',
            }
        with self.backend.work_on(self.model._name,
                                  timestamp=self.timestamp) as work:
            mapper = work.component(usage='export.mapper')
            self.assertDictEqual(mapper.map_record(self.product_18).values(),
                                 expected)

    def test_filename(self):
        today = fields.Date.today().replace('-', '')
        with self.backend.work_on(self.model._name,
                                  timestamp=self.timestamp) as work:
            writer = work.component(usage='local.xml.writer')
            self.assertEqual(
                writer.filename(), 'ProductStock_{}.xml'.format(today))

    @tools.mute_logger('dicttoxml')
    def test_record_exporter(self):
        """ Export, create xml file and compare with the one in example """
        self.timestamp.writer = 'local'
        # Pb with the next use date that changes everyday
        self.lot1.use_date = False
        self.lot2.use_date = False
        with self.backend.work_on(self.model._name,
                                  timestamp=self.timestamp) as work:
            exporter = work.component(usage='record.exporter.cron')
            respath = exporter.run()
        with open(respath, 'r') as result_file:
            result = result_file.read()
        self.assertXmlEquivalentData(
            result, self.read_test_file('stock_export_1.xml'), 'Sku')

    def test_differential_export(self):
        """ Test with timestamp, should return only one quant"""
        # Set timestamp to 1 day back
        self.timestamp.writer = 'local'
        d = (datetime.today() - timedelta(days=1)).strftime(
                "%Y-%m-%d %H:%M:%S")
        self.timestamp.last_export = d
        # Get items to export, there should be one
        with self.backend.work_on(self.model._name,
                                  timestamp=self.timestamp) as work:
            exporter = work.component(
                    usage='record.exporter.cron',
                    model_name=self.model._name
            )
            items = exporter.get_items(self.timestamp.last_export)
        self.assertEqual(len(items), 1)
