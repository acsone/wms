# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import os
from datetime import datetime, timedelta

import mock
import requests

from odoo.tests.common import SavepointCase


class ExportStockUpdateSingleTestCase(SavepointCase):
    def setUp(self):
        super(ExportStockUpdateSingleTestCase, self).setUp()
        os.environ["ODOO_ESB_WS_USER"] = "ws_user"
        os.environ["ODOO_ESB_WS_BASE_URL"] = "https://test.com"
        os.environ["ODOO_ESB_WS_PWD"] = "pwd"
        self.backend = self.env["esb.backend"].get_singleton()
        self.setup_records()
        self.maxDiff = None
        self.timestamp = self.env.ref("connector_esb.esb_timestamp_stock_update_single")

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
        self.prod1 = self.env.ref("product.product_product_20")
        self.prod1.default_code = "ref1"
        self.prod1.type = "product"
        self.prod1.sale_ok = True
        self.prod1.state_id = self.env.ref("specific_purchase.product_state_a")
        self.service = self.model.create(
            {"default_code": "TST", "name": "test product", "type": "service"}
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
        # Lets add some stock
        self.life_date_1 = datetime.today() + timedelta(weeks=40)
        self.life_date_2 = datetime.today() + timedelta(weeks=1)
        self.life_date_3 = datetime.today() + timedelta(days=1)
        self.lot1 = self.env["stock.production.lot"].create(
            {
                "product_id": self.prod1.id,
                "name": "lot1",
                "life_date": self.life_date_1.strftime("%Y-%m-%d %H:%M:%S"),
            }
        )
        self.lot2 = self.env["stock.production.lot"].create(
            {
                "product_id": self.prod1.id,
                "name": "lot2",
                "life_date": self.life_date_2.strftime("%Y-%m-%d %H:%M:%S"),
            }
        )
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

    def post_ret_status(url, data, headers, auth):
        resp = requests.Response()
        resp.status_code = 200
        resp.json = lambda: '{"erp_id" : "42", “increment_id” : “1000000348”}'
        return resp

    @mock.patch("requests.post", side_effect=post_ret_status)
    def test_record_exporter(self, post):
        """Test export of a product catching the post request."""
        with self.backend.work_on(self.model._name, timestamp=self.timestamp) as work:
            exporter = work.component(usage="record.exporter")
            exporter.run(self.prod1)
        post.assert_called_once()

    def test_product_ok_for_export(self):
        """Check product valid to be exported"""
        self.assertTrue(self.prod1._is_product_fit_to_export())

    def test_product_not_for_sale(self):
        """Product not for sale are not exported"""
        self.prod1.sale_ok = False
        self.assertEqual(self.prod1._is_product_fit_to_export(), False)

    def test_product_type_service(self):
        """Product of type other than product are not exported."""
        self.assertEqual(self.service._is_product_fit_to_export(), False)
