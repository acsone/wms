# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from unittest import mock

from odoo.tests.common import TransactionCase

from ..controllers.stock import StockController
from .common import MockRequest


class TestStockController(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        cls.product1 = cls.env["product.product"].create(
            {"name": "Product1", "default_code": "exportable001", "cnk_code": "000015"}
        )
        cls.product2 = cls.env["product.product"].create(
            {
                "name": "Product2",
                "default_code": "exportable002",
                "cnk_code": "000016",
            }
        )
        cls.product3 = cls.env["product.product"].create(
            {"name": "Product3", "default_code": "exportable003", "cnk_code": "000017"}
        )
        cls.all_records = cls.product1 + cls.product2 + cls.product3

    def test_cnk(self):
        product_product = self.env["product.product"]
        with (
            mock.patch.object(
                product_product.__class__, "get_cnk_products_domain"
            ) as mock_get_cnk_products_domain,
            MockRequest(self.env, session_info={"db": self.env.cr.dbname}),
        ):
            mock_get_cnk_products_domain.return_value = [
                ("id", "in", self.all_records.ids)
            ]
            result = StockController().product_stock_cnk()

        self.assertEqual(len(result), 3)
        self.assertEqual(
            result,
            [
                {"cnk": "000015", "quantity": 0.0, "pid": "exportable001"},
                {"cnk": "000016", "quantity": 0.0, "pid": "exportable002"},
                {"cnk": "000017", "quantity": 0.0, "pid": "exportable003"},
            ],
        )

    def test_sku(self):
        product_product = self.env["product.product"]
        with (
            mock.patch.object(
                product_product.__class__, "get_sku_products_domain"
            ) as mock_get_sku_products_domain,
            MockRequest(self.env, session_info={"db": self.env.cr.dbname}),
        ):
            mock_get_sku_products_domain.return_value = [
                ("id", "in", self.all_records.ids)
            ]
            result = StockController().product_stock_sku()
        self.assertEqual(len(result), 3)
        self.assertEqual(
            result,
            [
                {"quantity": 0.0, "sku": "exportable001"},
                {"quantity": 0.0, "sku": "exportable002"},
                {"quantity": 0.0, "sku": "exportable003"},
            ],
        )
