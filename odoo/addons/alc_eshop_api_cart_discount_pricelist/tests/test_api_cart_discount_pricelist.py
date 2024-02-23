# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import uuid

from odoo.addons.extendable_fastapi.tests.common import FastAPITransactionCase
from odoo.addons.shopinvader_api_cart.routers import cart_router


class TestSaleCartApi(FastAPITransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_1 = cls.env["product.product"].create(
            {
                "name": "product_1",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "list_price": 10,
            }
        )
        partner = cls.env["res.partner"].create({"name": "FastAPI Cart Demo"})

        cls.so = cls.env["sale.order"]._create_empty_cart(partner.id)
        cls.so.order_line = [
            (
                0,
                0,
                {
                    "product_id": cls.product_1.id,
                    "product_uom_qty": 1,
                    "product_uom": cls.product_1.uom_id.id,
                    "order_id": cls.so.id,
                },
            )
        ]
        cls.so.order_line.discount2 = 10
        cls.so.order_line.discount3 = 10

        discount_pricelist_5 = cls.env["product.pricelist"].create(
            {
                "name": "Unittest Discount Pricelist 5",
                "item_ids": [
                    (
                        0,
                        False,
                        {
                            "applied_on": "0_product_variant",
                            "product_id": cls.product_1.id,
                            "compute_price": "percentage",
                            "percent_price": 5,
                        },
                    )
                ],
            }
        )
        discount_pricelist_10 = cls.env["product.pricelist"].create(
            {
                "name": "Unittest Discount Pricelist 10",
                "item_ids": [
                    (
                        0,
                        False,
                        {
                            "applied_on": "0_product_variant",
                            "product_id": cls.product_1.id,
                            "compute_price": "percentage",
                            "percent_price": 10,
                            "min_quantity": 10,
                        },
                    )
                ],
            }
        )
        cls.discount_item_5 = discount_pricelist_5.item_ids
        cls.discount_item_10 = discount_pricelist_10.item_ids
        cls.so.discount_pricelist_ids = discount_pricelist_5 | discount_pricelist_10

        cls.default_fastapi_authenticated_partner = partner
        cls.default_fastapi_router = cart_router

    def test_discount_multiple_min_qty(self):
        cart_uuid = str(uuid.uuid4())
        with self._create_test_client() as test_client:
            response = test_client.post(
                "/sync",
                json={
                    "transactions": [
                        {
                            "uuid": cart_uuid,
                            "product_id": self.product_1.id,
                            "qty": 5,
                        }
                    ]
                },
            )
            self.assertEqual(response.status_code, 201)
            line = self.so.order_line
            self.assertEqual(self.discount_item_5, line.discount_item_id)
            self.assertEqual(5, line.discount3)

            response = test_client.post(
                "/sync",
                json={
                    "transactions": [
                        {
                            "uuid": cart_uuid,
                            "product_id": self.product_1.id,
                            "qty": 5,
                        }
                    ],
                },
            )
            self.assertEqual(response.status_code, 201)
            self.assertEqual(self.discount_item_10, line.discount_item_id)
            self.assertEqual(10, line.discount3)

            response = test_client.post(
                "/sync",
                json={
                    "transactions": [
                        {
                            "uuid": cart_uuid,
                            "product_id": self.product_1.id,
                            "qty": -5,
                        }
                    ]
                },
            )
            self.assertEqual(response.status_code, 201)
            line = self.so.order_line
            self.assertEqual(self.discount_item_5, line.discount_item_id)
            self.assertEqual(5, line.discount3)
