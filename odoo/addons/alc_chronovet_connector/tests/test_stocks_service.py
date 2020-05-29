# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import CommonCase


class TestStocksService(CommonCase):
    @classmethod
    def setUpClass(cls):
        super(TestStocksService, cls).setUpClass()

        with cls.work_on_services() as work:
            cls.stocks_service = work.component(usage="stocks")

    def test_00(self):
        """
        Data:
            1 saleable product
        Test case:
            Get the stock of all products
        Expected result:
            The product is into the list with the expected info
        """
        res = self.stocks_service.dispatch("search", params=False)
        self.assertEqual(res["size"], 1)
        result = res["data"][0]
        self.assertDictEqual(result, {"quantity": 5.0, "sku": "12345"})

    def test_01(self):
        """
        Data:
            1 saleable product
        Test case:
            Get the stock of a given products
        Expected result:
            The product is into the list with the expected info
        """
        sku = self.saleable_product.default_code
        res = self.stocks_service.dispatch("search", params=dict(skus=[sku]))
        self.assertEqual(res["size"], 1)
        result = res["data"][0]
        self.assertDictEqual(result, {"quantity": 5.0, "sku": "12345"})
        res = self.stocks_service.dispatch("search", params=dict(skus=[sku + "old"]))
        self.assertEqual(res["size"], 0)
