# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.fastapi.tests.common import FastAPITransactionCase

from ..routers import delivery_carriers_router


class TestDeliveryCarrierRouter(FastAPITransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_delivery_normal = cls.env["product.product"].create(
            {
                "name": "Normal Delivery Charges",
                "type": "service",
                "list_price": 10.0,
                "categ_id": cls.env.ref("delivery.product_category_deliveries").id,
            }
        )
        cls.carrier = cls.env["delivery.carrier"].create(
            {
                "name": "Normal Delivery Charges",
                "fixed_price": 10,
                "delivery_type": "fixed",
                "product_id": cls.product_delivery_normal.id,
            }
        )
        cls.carrier.available_in_website = True
        cls.default_fastapi_router = delivery_carriers_router
        cls.partner = cls.env["res.partner"].create({"name": "partner"})
        cls.cart = cls.env["sale.order"]._create_empty_cart(cls.partner.id)

    def test_search(self):
        with self._create_test_client(partner=self.partner) as test_client:
            response = test_client.get("/delivery_carriers")
            self.assertEqual(response.status_code, 200)
            res = response.json()
            self.assertEqual(len(res["data"]), 1)
            self.assertDictEqual(
                {
                    "id": self.carrier.id,
                    "name": self.carrier.name,
                },
                res["data"][0],
            )
            self.carrier.available_in_website = False
            response = test_client.get("/delivery_carriers")
            self.assertEqual(response.status_code, 200)
            res = response.json()
            self.assertEqual(len(res["data"]), 0)
