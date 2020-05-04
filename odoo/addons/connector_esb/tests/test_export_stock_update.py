# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import os
from datetime import datetime, timedelta

import requests

import mock
from odoo.tests.common import SavepointCase


class ExportStockUpdateTestCase(SavepointCase):
    def setUp(self):
        super(ExportStockUpdateTestCase, self).setUp()
        os.environ["ODOO_ESB_WS_USER"] = "ws_user"
        os.environ["ODOO_ESB_WS_BASE_URL"] = "https://test.com"
        os.environ["ODOO_ESB_WS_PWD"] = "pwd"
        self.backend_model = self.env["esb.backend"]
        self.backend = self.backend_model.get_singleton()
        self.setup_records()
        self.maxDiff = None
        self.timestamp = self.env.ref("connector_esb.esb_timestamp_stock_update")

    @property
    def model(self):
        return self.env["product.product"]

    def setup_records(self):
        # Remove all product from sale so they do not interfere
        products = self.env["stock.quant"].search([]).mapped("product_id")
        products.write({"sale_ok": False})
        self.partner = self.env.ref("base.res_partner_1")
        self.loc_physical = self.env.ref("specific_base.stock_location_vlb")
        self.location = self.env.ref("stock.stock_location_stock")
        self.location.location_id = self.loc_physical
        self.location._parent_store_compute()
        # Two products that should be picked up for export
        self.prod1 = self.env.ref("product.product_product_20")
        self.prod1.default_code = "ref1"
        self.prod1.type = "product"
        self.prod1.sale_ok = True
        self.prod1.state_id = self.env.ref("specific_purchase.product_state_a")
        self.prod2 = self.env["product.product"].create(
            {
                "name": "test prod 2",
                "default_code": "test prod 2",
                "type": "product",
                "sale_ok": True,
            }
        )
        # And product without Sku, not to be exported
        self.prod3 = self.env["product.product"].create(
            {
                "name": "test prod 3",
                "default_code": "",
                "type": "product",
                "sale_ok": True,
            }
        )
        # Product service not to be exported
        self.prod4 = self.env["product.product"].create(
            {
                "name": "test prod 4",
                "default_code": "ref4",
                "type": "service",
                "sale_ok": True,
            }
        )
        # Product not ok for sale, not to be exported
        self.prod5 = self.env["product.product"].create(
            {
                "name": "test prod 5",
                "default_code": "ref5",
                "type": "product",
                "sale_ok": False,
            }
        )
        # Add a sale order to test the sale_average
        self.so0 = self.env["sale.order"].create(
            {
                "esb_ref": "ref_123",
                "partner_id": self.partner.id,
                "sale_channel": "fax",
                "client_order_ref": "whatever the client want",
                "delivery_price": 23.5,
                "suite_name": "0123434234",
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "sequence": 1,
                            "name": "prod 1",
                            "product_id": self.prod1.id,
                            "product_uom_qty": 55,
                        },
                    )
                ],
            }
        )
        # And add a canceled sale order that should not be part of the
        # sales_average computation
        self.so1 = self.env["sale.order"].create(
            {
                "esb_ref": "ref_124",
                "partner_id": self.partner.id,
                "sale_channel": "fax",
                "client_order_ref": "whatever the client want",
                "delivery_price": 23.5,
                "suite_name": "0123434234",
                "state": "cancel",
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "sequence": 1,
                            "name": "prod 1",
                            "product_id": self.prod1.id,
                            "product_uom_qty": 7,
                        },
                    )
                ],
            }
        )
        # Add an older sale order that should not be picked up
        self.so2 = self.env["sale.order"].create(
            {
                "esb_ref": "ref_12388734",
                "partner_id": self.partner.id,
                "sale_channel": "fax",
                "client_order_ref": "whatever the client want",
                "delivery_price": 23.5,
                "suite_name": "0123434234",
                "date_order": "2017-10-10",
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "sequence": 1,
                            "name": "prod 1",
                            "product_id": self.prod1.id,
                            "product_uom_qty": 55,
                        },
                    )
                ],
            }
        )
        # Lets add some lots
        self.life_date_0 = datetime.today() + timedelta(days=3)
        self.life_date_1 = datetime.today() + timedelta(weeks=40)
        self.life_date_2 = datetime.today() + timedelta(weeks=1)
        self.life_date_3 = datetime.today() + timedelta(days=1)
        self.lot0 = self.env["stock.production.lot"].create(
            {
                "product_id": self.prod1.id,
                "name": "lot0",
                "life_date": self.life_date_0.strftime("%Y-%m-%d %H:%M:%S")
                # product_qty: 0
            }
        )

        self.lot1 = self.env["stock.production.lot"].create(
            {
                "product_id": self.prod1.id,
                "name": "lot1",
                "life_date": self.life_date_1.strftime("%Y-%m-%d %H:%M:%S")
                # product_qty: 100
            }
        )

        self.lot2 = self.env["stock.production.lot"].create(
            {
                "product_id": self.prod1.id,
                "name": "lot2",
                "life_date": self.life_date_2.strftime("%Y-%m-%d %H:%M:%S")
                # product_qty: 100
            }
        )

        # mock some quantities
        # lot0 is there to ensure it is not picking a zero qty lot
        def mock_product_qty(rs):
            for rec in rs:
                if rec.name == "lot0":
                    qty = 0.0
                else:
                    qty = 100.0
                rec.product_qty = qty

        self.env["stock.production.lot"]._patch_method("_product_qty", mock_product_qty)
        inventory_wizard = self.env["stock.change.product.qty"].create(
            {
                "product_id": self.prod1.id,
                "new_quantity": 50.0,
                "location_id": self.location.id,
                "lot_id": self.lot2.id,
            }
        )
        inventory_wizard.change_product_qty()
        inventory_wizard = self.env["stock.change.product.qty"].create(
            {
                "product_id": self.prod1.id,
                "new_quantity": 25.0,
                "location_id": self.location.id,
                "lot_id": self.lot1.id,
            }
        )
        inventory_wizard.change_product_qty()
        # Add another product to see that it does not interfere
        self.lot_p2 = self.env["stock.production.lot"].create(
            {
                "product_id": self.prod2.id,
                "name": "lot_p2",
                "life_date": self.life_date_3.strftime("%Y-%m-%d %H:%M:%S")
                # product_qty: 100
            }
        )
        inventory_wizard = self.env["stock.change.product.qty"].create(
            {
                "product_id": self.prod2.id,
                "new_quantity": 25.0,
                "location_id": self.location.id,
                "lot_id": self.lot_p2.id,
            }
        )
        inventory_wizard.change_product_qty()

    def test_mapper(self):
        """ Generate data dict with mapper and check with what is expected """
        product = self.prod1
        expected = {
            "sku": u"ref1",
            "qty": product.immediately_usable_qty,
            "sales_average": round(55.0 / 365, 1),
            "erp_stock_code": u"A",
            "date_peremption": self.life_date_2.strftime("%Y-%m-%d"),
        }
        with self.backend.work_on(self.model._name, timestamp=self.timestamp) as work:
            mapper = work.component(usage="export.mapper")
            values = mapper.map_record(product).values()
        self.assertDictEqual(values, expected)

    def test_product_pickedup(self):
        """Check the exporter takes the two product with changed stock """
        with self.backend.work_on(self.model._name, timestamp=self.timestamp) as work:
            exporter = work.component(usage="record.exporter.cron")
            items = exporter.get_items(None)
        self.assertEqual(len(items.mapped("product_id")), 2)

    def test_product_no_sku(self):
        """Product without Sku should not be picked up."""
        inventory_wizard = self.env["stock.change.product.qty"].create(
            {
                "product_id": self.prod3.id,
                "new_quantity": 4325.0,
                "location_id": self.location.id,
            }
        )
        inventory_wizard.change_product_qty()
        with self.backend.work_on(self.model._name, timestamp=self.timestamp) as work:
            exporter = work.component(usage="record.exporter.cron")
            items = exporter.get_items(None)
        self.assertEqual(len(items.mapped("product_id")), 2)

    def test_product_type_service(self):
        """Product of type other than product should not be picked up."""
        inventory_wizard = self.env["stock.change.product.qty"].create(
            {
                "product_id": self.prod4.id,
                "new_quantity": 9945.0,
                "location_id": self.location.id,
            }
        )
        inventory_wizard.change_product_qty()
        with self.backend.work_on(self.model._name, timestamp=self.timestamp) as work:
            exporter = work.component(usage="record.exporter.cron")
            items = exporter.get_items(None)
        self.assertEqual(len(items.mapped("product_id")), 2)

    def test_product_not_ok_for_sale(self):
        """Product not for sale should not be picked up"""
        inventory_wizard = self.env["stock.change.product.qty"].create(
            {
                "product_id": self.prod5.id,
                "new_quantity": 2395.0,
                "location_id": self.location.id,
            }
        )
        inventory_wizard.change_product_qty()
        with self.backend.work_on(self.model._name, timestamp=self.timestamp) as work:
            exporter = work.component(usage="record.exporter.cron")
            items = exporter.get_items(None)
        self.assertEqual(len(items.mapped("product_id")), 2)

    def post_ret_status(url, data, headers, auth):
        resp = requests.Response()
        resp.status_code = 200
        resp.json = lambda: '{"status" : "OK", “code” : “200”, "items": []}'
        return resp

    @mock.patch("requests.post", side_effect=post_ret_status)
    def test_record_exporter(self, post):
        """Test export of a sale order catching the post request."""
        with self.backend.work_on(self.model._name, timestamp=self.timestamp) as work:
            exporter = work.component(usage="record.exporter.cron")
            exporter.run()
        post.assert_called_once()
