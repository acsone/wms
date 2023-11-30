# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from fastapi import status
from requests import Response

from ..routers.products import router as products_router
from .common import CommonB2CServiceCase


class TestProductsService(CommonB2CServiceCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.default_fastapi_router = products_router

    def test_00(self):
        """
        Data:

            1 saleable product
        Test case:
            Get list of saleable product
        Expected result:
            The product is into the list with the expected info
        """
        with self._create_test_client() as client:
            response: Response = client.get(
                "/products/search", headers={"api-key": "1234"}
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())
        res = response.json()
        self.assertEqual(res["size"], 2)
        result = res["data"][0]
        result.pop("create_date")
        self.assertDictEqual(
            result,
            {
                "eans": ["XXX0001"],
                "name": "Product 1",
                "price": 10.0,
                "quantity": 5.0,
                "sku": "12345",
                "cnk": "CNK123",
                "taxes": [{"amount": 6.0, "amount_type": "percent", "name": "Tax 6%"}],
            },
        )
        result = res["data"][1]
        result.pop("create_date")
        self.assertDictEqual(
            result,
            {
                "eans": ["XXX0002"],
                "name": "Product 2",
                "price": 20.0,
                "quantity": 110.0,
                "sku": "23456",
                "cnk": "CNK234",
                "taxes": [
                    {
                        "amount": 10.0,
                        "amount_type": "fixed",
                        "name": "Tax 10.0 (Fixed)",
                    }
                ],
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
        with self._create_test_client() as client:
            response: Response = client.get(
                "/products/search", headers={"api-key": "1234"}
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())
        res = response.json()
        self.assertEqual(res["size"], 2)
        result = res["data"][0]
        result.pop("create_date")
        self.assertDictEqual(
            result,
            {
                "eans": [],
                "name": "Product 1",
                "price": 10.0,
                "quantity": 5.0,
                "sku": "12345",
                "cnk": None,
                "taxes": [{"amount": 6.0, "amount_type": "percent", "name": "Tax 6%"}],
            },
        )
        result = res["data"][1]
        result.pop("create_date")
        self.assertDictEqual(
            result,
            {
                "eans": ["XXX0002"],
                "name": "Product 2",
                "price": 20.0,
                "quantity": 110.0,
                "sku": "23456",
                "cnk": "CNK234",
                "taxes": [
                    {
                        "amount": 10.0,
                        "amount_type": "fixed",
                        "name": "Tax 10.0 (Fixed)",
                    }
                ],
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
        with self._create_test_client() as client:
            for categ_xml_id in (
                "alc_product_category_data.product_categ_humain",
                "alc_product_category_data.product_categ_vet_belges",
                "alc_product_category_data.product_categ_importation",
            ):
                self.saleable_product.categ_id = self.env.ref(categ_xml_id)
                response: Response = client.get(
                    "/products/search", headers={"api-key": "1234"}
                )
                self.assertEqual(
                    response.status_code, status.HTTP_200_OK, response.json()
                )
                res = response.json()
                self.assertEqual(res["size"], 1)
                self.assertEqual(
                    res["data"][0]["sku"], self.saleable_product_2.default_code
                )
            self.saleable_product.categ_id = default_categ
            response: Response = client.get(
                "/products/search", headers={"api-key": "1234"}
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())
            res = response.json()
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
        with self._create_test_client() as client:
            response: Response = client.get(
                "/products/search",
                headers={"api-key": "1234"},
                params={"skus[]": [sku]},
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())
        res = response.json()
        self.assertEqual(res["size"], 1)
        with self._create_test_client() as client:
            response: Response = client.get(
                "/products/search",
                headers={"api-key": "1234"},
                params={"skus[]": [sku + "false"]},
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())
        res = response.json()
        self.assertEqual(res["size"], 0)
