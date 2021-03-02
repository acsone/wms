# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import os

from .common import ESBXMLTestCase


class ExportProductPriceTestCase(ESBXMLTestCase):
    def setUp(self):
        super(ExportProductPriceTestCase, self).setUp()
        self.setup_records()
        self.maxDiff = None
        self.timestamp = self.env.ref("connector_esb.esb_timestamp_product_price")

    @property
    def model(self):
        return self.env["product.product"]

    def setup_records(self):
        # Set existing products to not for sale, as to not bother the tests
        self.env["product.product"].search([]).write({"sale_ok": False})
        # # Create 2 good products
        self.p1 = self.env["product.product"].create(
            {
                "name": "Unittest P1",
                "default_code": "0001",
                "list_price": "12.7",
                "type": "product",
                "sale_ok": True,
            }
        )
        self.p1.indicated_price = 0
        self.p2 = self.env["product.product"].create(
            {
                "name": "Unittest P2",
                "default_code": "0002",
                "list_price": "82.7",
                "type": "product",
                "sale_ok": True,
            }
        )
        self.p2.indicated_price = 12
        self.pricelist_pb2 = self.env.ref("specific_data.product_pricelist_pb2")
        self.pricelist_pb2.item_ids = [
            (
                0,
                False,
                {
                    "applied_on": "1_product",
                    "product_id": self.p1.id,
                    "compute_price": "fixed",
                    "fixed_price": 33.24,
                    "product_tmpl_id": self.p1.product_tmpl_id.id,
                },
            ),
            (
                0,
                False,
                {
                    "applied_on": "1_product",
                    "product_id": self.p2.id,
                    "compute_price": "fixed",
                    "fixed_price": 18.88,
                    "product_tmpl_id": self.p2.product_tmpl_id.id,
                },
            ),
        ]
        # And product without Sku, not to be exported
        self.p3 = self.env.ref("product.product_product_3")
        self.p3.type = "product"
        self.p3.default_code = ""
        self.p3.sale_ok = True
        # Product service not to be exported
        self.p4 = self.env.ref("product.product_product_4")
        self.p4.type = "service"
        self.p4.default_code = "ref4"
        self.p4.sale_ok = True

    def test_filename(self):
        self.check_filename("ProductPrice_{0}.xml")

    def test_mapper(self):
        """ Testing the mapper on one record"""
        expected = {
            "Sku": u"0001",
            "Price": "12.70",
            "Msrp": "0.00",
            "PharmacyPrice": "33.240",
        }
        self.p1.sale_price_2_export = 33.240
        self.timestamp.writer = "local"
        with self.backend.work_on(self.model._name, timestamp=self.timestamp) as work:
            mapper = work.component(usage="export.mapper")
            rec = self.p1
            self.assertDictEqual(mapper.map_record(rec).values(), expected)

    def test_export(self):
        """ Make a full export check with existing xml file"""
        self.timestamp.writer = "local"
        with self.backend.work_on(self.model._name, timestamp=self.timestamp) as work:
            exporter = work.component(usage="record.exporter.cron")
        exporter.update_saleprice_2()
        respath, _ = exporter.run()
        self.addCleanup(os.remove, respath)
        with open(respath, "r") as result_file:
            result = result_file.read()
        self.assertXmlEquivalentData(
            result, self.read_test_file("product_price_export_1.xml"), "Sku"
        )

    def test_product_pickedup(self):
        """Check the exporter takes the two product only"""
        with self.backend.work_on(self.model._name, timestamp=self.timestamp) as work:
            exporter = work.component(usage="record.exporter.cron")
            items = exporter.get_items(None)
        self.assertEqual(len(items), 2)
