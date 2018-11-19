# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import mock
import os
import random
import requests

from datetime import datetime, timedelta

from odoo.tests.common import SavepointCase


class ExportStockUpdateTestCase(SavepointCase):

    def setUp(self):
        super(ExportStockUpdateTestCase, self).setUp()
        os.environ['ODOO_ESB_WS_USER'] = 'ws_user'
        os.environ['ODOO_ESB_WS_BASE_URL'] = 'https://test.com'
        os.environ['ODOO_ESB_WS_PWD'] = 'pwd'
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
        # Create 20 products
        self.all_products = []
        for product_id in range(100, 110):
            self.all_products.append(self.env['product.product'].create({
                'name': 'test prod {}'.format(product_id),
                'default_code': 'test prod {}'.format(product_id),
                'type': 'product',
                'sale_ok': True,
            }))
        # Remove all product from sale so they do not interfere
        products = self.env['stock.quant'].search([]).mapped('product_id')
        products.write({'sale_ok': False})

        self.location = self.env.ref('stock.stock_location_stock').id

    def set_quant_write_date(self, quant_id, write_date):
        """Set the write_date on a quant."""
        self.env.cr.execute("""
            UPDATE stock_quant SET write_date = %s WHERE id = %s
        """, (write_date, quant_id))

    def update_timestamp_for_basic_lock(self, timestamp, exporter):
        """ """
        return (
            datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S") +
            timedelta(seconds=exporter.BASIC_LOCK_TIME + 1)
        ).strftime("%Y-%m-%d %H:%M:%S")

    def post_ret_status(url, data, headers, auth):
        resp = requests.Response()
        resp.status_code = 200
        resp.json = lambda: '{"status" : "OK", “code” : “200”, "items": []}'
        return resp

    @mock.patch('requests.post', side_effect=post_ret_status)
    def test_all_quants_in_same_second_are_exported(self, post):
        """
        Check with a split with quants in same second.
        And check that all are exported if nb of export is smaller
        than max records
        """
        # Make quants for the first 9 products in an older date
        for product in self.all_products[:-1]:
            inventory_wizard = self.env['stock.change.product.qty'].create({
                'product_id': product.id,
                'new_quantity': random.randint(1, 100),
                'location_id': self.location,
            })
            inventory_wizard.change_product_qty()
            self.set_quant_write_date(
                self.env['stock.quant'].search(
                    [('product_id.id', '=', product.id)])[0].id,
                '2017-11-05 12:00:00'
            )
        # All quants in the same second so all must be exported
        with self.backend.work_on(self.model._name,
                                  timestamp=self.timestamp) as work:
            exporter = work.component(usage='record.exporter.cron')
            exported_until = exporter.run(max_records=3)
            assert exported_until is None
        # Add a quant in a more recent date
        inventory_wizard = self.env['stock.change.product.qty'].create({
            'product_id': self.all_products[-1].id,
            'new_quantity': random.randint(1, 100),
            'location_id': self.location,
        })
        inventory_wizard.change_product_qty()
        # Must be done in two export if max_records is smaller than all records
        with self.backend.work_on(self.model._name,
                                  timestamp=self.timestamp) as work:
            exporter = work.component(usage='record.exporter.cron')
            # First export
            exported_until = exporter.run(max_records=3)
            assert exported_until == self.update_timestamp_for_basic_lock(
                    '2017-11-05 12:00:00', exporter)
            # Second export
            exported_until = exporter.run(
                export_since=exported_until,
                max_records=3
            )
            assert exported_until is None
            # But if max_records is larger it should export all in one go
            exported_until = exporter.run(
                export_since=exported_until,
                max_records=13
            )
            assert exported_until is None

    @mock.patch('requests.post', side_effect=post_ret_status)
    def test_quants_exports_are_split_2(self, post):
        """
        Check with a split with quants in different second.
        """
        # Make quants for the first 3 in an older date
        for product in self.all_products[:3]:
            inventory_wizard = self.env['stock.change.product.qty'].create({
                'product_id': product.id,
                'new_quantity': random.randint(1, 100),
                'location_id': self.location,
            })
            inventory_wizard.change_product_qty()
            self.set_quant_write_date(
                self.env['stock.quant'].search(
                    [('product_id.id', '=', product.id)])[0].id,
                '2017-11-05 12:00:00'
            )
        # Make quants for the next 3 for now
        for product in self.all_products[3:6]:
            inventory_wizard = self.env['stock.change.product.qty'].create({
                'product_id': product.id,
                'new_quantity': random.randint(1, 100),
                'location_id': self.location,
            })
            inventory_wizard.change_product_qty()
        with self.backend.work_on(self.model._name,
                                  timestamp=self.timestamp) as work:
            exporter = work.component(usage='record.exporter.cron')
            exported_until = exporter.run(max_records=3)
        assert exported_until is not None
        with self.backend.work_on(self.model._name,
                                  timestamp=self.timestamp) as work:
            exporter = work.component(usage='record.exporter.cron')
            exported_until = exporter.run(
                export_since=exported_until,
                max_records=3
            )
        assert exported_until is None
