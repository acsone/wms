# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from fastapi import status
from freezegun import freeze_time
from requests import Response

from ..routers.stocks import router as stocks_router
from .common import CommonB2CServiceCase


class TestStocksService(CommonB2CServiceCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.default_fastapi_router = stocks_router

    @freeze_time("2020-05-28 11:45:47")
    def test_00(self):
        """
        Data:

            2 saleable product
        Test case:
            Get the stock of all products
        Expected result:
            The product is into the list with the expected info
        """
        with self._create_test_client() as client:
            response: Response = client.get(
                "/stocks/search", headers={"api-key": "1234"}
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())
        res = response.json()
        self.assertEqual(res["size"], 2)
        result = res["data"][0]
        result.pop("create_date")
        self.assertDictEqual(
            result,
            {
                "cnk": "CNK123",
                "eans": ["XXX0001"],
                "name": "Product 1",
                "price": 10.0,
                "quantity": 5.0,
                "sku": "12345",
                "taxes": [{"amount": 6.0, "amount_type": "percent", "name": "Tax 6%"}],
            },
        )
        result = res["data"][1]
        result.pop("create_date")
        self.assertDictEqual(
            result,
            {
                "cnk": "CNK234",
                "eans": ["XXX0002"],
                "name": "Product 2",
                "price": 20.0,
                "quantity": 110.0,
                "sku": "23456",
                "taxes": [
                    {"amount": 10.0, "amount_type": "fixed", "name": "Tax 10.0 (Fixed)"}
                ],
            },
        )

    def test_01(self):
        """
        Data:

            2 saleable product
        Test case:
            Get the stock of a given products
        Expected result:
            The product is into the list with the expected info
        """
        sku = self.saleable_product.default_code
        with self._create_test_client() as client:
            response: Response = client.get(
                "/stocks/search",
                headers={"api-key": "1234"},
                params={"skus": [sku]},
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())
        res = response.json()
        self.assertEqual(res["size"], 1)
        result = res["data"][0]
        result.pop("create_date")
        self.assertDictEqual(
            result,
            {
                "cnk": "CNK123",
                "eans": ["XXX0001"],
                "name": "Product 1",
                "price": 10.0,
                "quantity": 5.0,
                "sku": "12345",
                "taxes": [{"amount": 6.0, "amount_type": "percent", "name": "Tax 6%"}],
            },
        )
        with self._create_test_client() as client:
            response: Response = client.get(
                "/stocks/search",
                headers={"api-key": "1234"},
                params={"skus": [sku + "old"]},
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())
        res = response.json()
        self.assertEqual(res["size"], 0)
