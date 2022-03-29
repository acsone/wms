# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.sale_cart_rest_api.tests.common import TestSaleCartRestApiCase


class TestSaleCartRestApi(TestSaleCartRestApiCase):
    @classmethod
    def setUpClass(cls):
        super(TestSaleCartRestApi, cls).setUpClass()
        cls.inventory_model = cls.env["stock.inventory"]
        cls.inventory_line_model = cls.env["stock.inventory.line"]
        cls.stock_location = cls.env.ref("stock.stock_location_stock")

        with cls.cart_service(cls.partner_1.id) as cart:
            info = cart.sync(
                uuid=None,
                transactions=[
                    {"uuid": "uuid1", "product_id": cls.product_1.id, "qty": 1}
                ],
            )
            cls.cart = cart
            cls.so = cls.env["sale.order"].browse(info["id"])

    def _define_product_qty(self, product, quantity):
        self.inventory = self.inventory_model.create(
            {
                "name": "Unittest Inventory",
                "location_id": self.stock_location.id,
                "filter": "partial",
            }
        )
        self.inventory.prepare_inventory()

        self.inventory_line_model.create(
            {
                "inventory_id": self.inventory.id,
                "product_id": product.id,
                "location_id": self.stock_location.id,
                "product_qty": quantity,
            }
        )
        self.inventory.action_done()

    def test_qty_unavailable(self):
        info = self.cart.dispatch(
            "sync", params={"uuid": self.so.uuid, "transactions": []},
        )
        # not product in stock
        self.assertEqual(1.0, info["lines"][0]["qty_unavailable"])

        # add product in stock
        self._define_product_qty(self.product_1, 10)
        info = self.cart.dispatch(
            "refresh_qty_unavailable", params={"uuid": self.so.uuid}
        )
        self.assertEqual(0.0, info["lines"][0]["qty_unavailable"])
        self.assertEqual(-1.0, info["lines"][0]["qty_unavailable_diff"])
