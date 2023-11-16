# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.addons.extendable_fastapi.tests.common import FastAPITransactionCase

from ..routers import carts_router


class TestSaleCartApi(FastAPITransactionCase):
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
        cls.product_1 = cls.env["product.product"].create(
            {
                "name": "product_1",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "type": "product",
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

        cls.default_fastapi_authenticated_partner = partner
        cls.default_fastapi_router = carts_router

    def test_set_delivery_method(self):
        with self._create_test_client() as test_client:
            response = test_client.post(
                "/carts/set_delivery_method",
                json={
                    "method_id": self.carrier.id,
                },
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.so.carrier_id, self.carrier)
