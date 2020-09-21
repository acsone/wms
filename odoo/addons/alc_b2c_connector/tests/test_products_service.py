# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import pytz

from .common import CommonCase


class TestProductsService(CommonCase):
    @classmethod
    def setUpClass(cls):
        super(TestProductsService, cls).setUpClass()

        with cls.work_on_services() as work:
            cls.products_service = work.component(usage="products")

    def test_00(self):
        """
        Data:
            1 saleable product
        Test case:
            Get list of saleable product
        Expected result:
            The product is into the list with the expected info
        """

        res = self.products_service.dispatch("search", params=False)
        self.assertEqual(res["size"], 2)
        result = res["data"][0]
        create_date = result.pop("create_date")
        self.assertEqual(create_date.tzinfo, pytz.utc)
        self.assertDictEqual(
            result,
            {
                "eans": [u"XXX0001"],
                "name": u"Product 1",
                "price": 10.0,
                "quantity": 5.0,
                "sku": u"12345",
                "cnk": "CNK123",
            },
        )
        result = res["data"][1]
        result.pop("create_date")
        self.assertDictEqual(
            result,
            {
                "eans": [u"XXX0002"],
                "name": u"Product 2",
                "price": 20.0,
                "quantity": 110.0,
                "sku": u"23456",
                "cnk": "CNK234",
            },
        )

    def test_01(self):
        """
        Data:
            1 saleable product without cnk nor ean
        Test case:
            Get list of saleable product
        Expected result:
            The product is into the list with the expected info
        """
        self.saleable_product.write({"barcode": False, "cnk_code": False})
        res = self.products_service.dispatch("search", params=False)
        self.assertEqual(res["size"], 2)
        result = res["data"][0]
        create_date = result.pop("create_date")
        self.assertEqual(create_date.tzinfo, pytz.utc)
        self.assertDictEqual(
            result,
            {
                "eans": [],
                "name": u"Product 1",
                "price": 10.0,
                "quantity": 5.0,
                "sku": u"12345",
                "cnk": None,
            },
        )
        result = res["data"][1]
        result.pop("create_date")
        self.assertDictEqual(
            result,
            {
                "eans": [u"XXX0002"],
                "name": u"Product 2",
                "price": 20.0,
                "quantity": 110.0,
                "sku": u"23456",
                "cnk": "CNK234",
            },
        )

    def test_02(self):
        """
        Data:
            2 saleable product
        Test case:
            Put 1 the product into a forbidden category
        Expected result:
            This product is no more into the list with the expected info
        """
        default_categ = self.saleable_product.categ_id
        for categ_xml_id in (
            "specific_data.product_categ_humain",
            "specific_data.product_categ_vet_belges",
            "specific_data.product_categ_importation",
        ):
            self.saleable_product.categ_id = self.env.ref(categ_xml_id)
            res = self.products_service.dispatch("search", params=False)
            self.assertEqual(res["size"], 1)
            self.assertEqual(
                res["data"][0]["sku"], self.saleable_product_2.default_code
            )
        self.saleable_product.categ_id = default_categ
        res = self.products_service.dispatch("search", params=False)
        self.assertEqual(res["size"], 2)

    def test_03(self):
        """
        Data:
            3 saleable product
        Test case:
            Search for a given sku
        Expected result:
            Product is returned if the sku match
        """
        sku = self.saleable_product.default_code
        res = self.products_service.dispatch("search", params=dict(skus=[sku]))
        self.assertEqual(res["size"], 1)
        res = self.products_service.dispatch(
            "search", params=dict(skus=[sku + "false"])
        )
        self.assertEqual(res["size"], 0)
