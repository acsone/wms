# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import os
import random

import mock
import requests

from odoo.tests.common import SavepointCase

from odoo.addons.connector.exception import ConnectorException


def successful_post_response(url, data, headers, auth):
    resp = requests.Response()
    resp.status_code = 200
    resp.json = lambda: '{"status" : "OK", “code” : “200”, "items": []}'
    return resp


def failing_post_response(url, data, headers, auth):
    """ This makes the http post fail when product 103 is in the data."""
    if "test prod 103" in data:
        raise ConnectorException("Failed push")
    resp = requests.Response()
    resp.status_code = 200
    resp.json = lambda: '{"status" : "OK", “code” : “200”, "items": []}'
    return resp


class ExportStockUpdateTestCase(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(ExportStockUpdateTestCase, cls).setUpClass()
        os.environ["ODOO_ESB_WS_USER"] = "ws_user"
        os.environ["ODOO_ESB_WS_BASE_URL"] = "https://test.com"
        os.environ["ODOO_ESB_WS_PWD"] = "pwd"
        cls.backend_model = cls.env["esb.backend"]
        cls.backend = cls.backend_model.get_singleton()
        cls.setup_records()
        cls.maxDiff = None
        cls.timestamp = cls.env.ref("connector_esb.esb_timestamp_stock_update")

    @property
    def model(self):
        return self.env["product.product"]

    @classmethod
    def setup_records(cls):
        cls.location = cls.env.ref("stock.stock_location_stock").id
        # Remove all existing product from sale so they do not interfere
        products = cls.env["stock.quant"].search([]).mapped("product_id")
        products.write({"sale_ok": False})
        # Create 10 products
        cls.all_products = cls.env["product.product"]
        for product_code in range(100, 110):
            cls.all_products |= cls.env["product.product"].create(
                {
                    "name": "test prod {}".format(product_code),
                    "default_code": "test prod {}".format(product_code),
                    "type": "product",
                    "sale_ok": True,
                }
            )
        cls.product_ids = cls.all_products.ids
        # Add a quant for each product
        for product in cls.all_products:
            inventory_wizard = cls.env["stock.change.product.qty"].create(
                {
                    "product_id": product.id,
                    "new_quantity": random.randint(1, 100),
                    "location_id": cls.location,
                }
            )
            inventory_wizard.change_product_qty()

    def set_quant_write_date(self, quants, write_date):
        """Set the write_date on some quants."""
        self.env.cr.execute(
            "UPDATE stock_quant SET write_date = %s WHERE id in %s",
            (write_date, tuple(quants.ids)),
        )
        quants.refresh()

    @mock.patch("requests.post", side_effect=successful_post_response)
    def test_successful_export(self, post):
        """
        Check with a split with quants in same second.
        And check that all are exported if nb of export is smaller
        than max records
        """
        with self.backend.work_on(self.model._name, timestamp=self.timestamp) as work:
            exporter = work.component(usage="record.exporter.cron")
            # 10 product stock status to export by batch of 3, is 4 export
            exported_until = exporter.run(max_records=3)
            self.assertEqual(exported_until, None)
            self.assertEqual(post.call_count, 4)
            # 10 product stock status to export by batch of 5, is 2 export
            exported_until = exporter.run(max_records=5)
            self.assertEqual(exported_until, None)
            self.assertEqual(post.call_count, 4 + 2)
            # 10 product stock status with no limit
            exported_until = exporter.run(max_records=0)
            self.assertEqual(exported_until, None)
            self.assertEqual(post.call_count, 4 + 2 + 1)

    @mock.patch("requests.post", side_effect=failing_post_response)
    def test_failing_export_1(self, post):
        """ Check failed push to ESB after a successfull one.

        A failed post to the ESB after some successful ones, should return
        as timestamp the write_date of the last exported quant plus the
        basic lock safety seconds.

        """
        # Set three quants in an older date, but not the one for product 103
        quants = self.env["stock.quant"].search(
            [("product_id", "in", self.product_ids[0:3])]
        )
        self.set_quant_write_date(quants, "2017-11-05 12:00:00")
        # set the quant of product 103 at a slightly later date, so that we are
        # sure it is exported in the 2nd batch of 3
        quants = self.env["stock.quant"].search(
            [("product_id", "=", self.product_ids[3])]
        )
        self.set_quant_write_date(quants, "2017-11-06 12:00:00")
        with self.backend.work_on(self.model._name, timestamp=self.timestamp) as work:
            exporter = work.component(usage="record.exporter.cron")
            exported_until = exporter.run(max_records=3)
            # Failing after the second export
            self.assertEqual(post.call_count, 2)
            self.assertEqual(
                exported_until, exporter.get_exported_until("2017-11-05 12:00:00")
            )

    @mock.patch("requests.post", side_effect=failing_post_response)
    def test_failing_export_2(self, post):
        """ Check export that fails at the first push to the ESB

        When the first HTTP post to the ESB fails the export must return
        an exception.
        """
        # Set three quants in an older date including the one for product 103
        quants = self.env["stock.quant"].search(
            [("product_id", "in", self.product_ids[3:5])]
        )
        self.set_quant_write_date(quants, "2017-11-05 12:00:00")
        with self.backend.work_on(self.model._name, timestamp=self.timestamp) as work:
            exporter = work.component(usage="record.exporter.cron")
            with self.assertRaises(ConnectorException):
                exporter.run(max_records=3)
            self.assertEqual(post.call_count, 1)

    @mock.patch("requests.post", side_effect=successful_post_response)
    def test_nothing_to_export(self, post):
        """ Check an export that has nothing to do.

        When there is nothing to do the exporter will return None.
        """
        # Set all quants in an older date than the export_since params
        quants = self.env["stock.quant"].search([])
        self.set_quant_write_date(quants, "2017-11-05 12:00:00")
        with self.backend.work_on(self.model._name, timestamp=self.timestamp) as work:
            exporter = work.component(usage="record.exporter.cron")
            exported_until = exporter.run(
                max_records=3, export_since="2017-12-12 12:00:00"
            )
            self.assertEqual(post.call_count, 0)
            self.assertEqual(exported_until, None)
