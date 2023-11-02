# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from fastapi import FastAPI

from odoo.addons.shopinvader_api_cart.routers import cart

from ..routers import carts_router
from .common import TestSaleCartRestApiInfoCase


class TestSaleCartRestApiInfo(TestSaleCartRestApiInfoCase):
    def test_update(self):
        # ensure the api works when mixed with the native api
        app = FastAPI()
        app.include_router(carts_router)
        app.include_router(cart.cart_router, prefix="/carts")
        with self._create_test_client(app=app) as test_client:
            response = test_client.post(
                "carts/info", json={"customer_ref": "my_ref", "note": "my note"}
            )
            self.assertEqual(205, response.status_code)
            self.assertEqual("my_ref", self.so.client_order_ref)
            self.assertEqual("<p>my note</p>", self.so.note)

            response = test_client.post(
                f"carts/{self.so.uuid}/info",
                json={"customer_ref": "my_other_ref", "note": "my other note"},
            )
            self.assertEqual(205, response.status_code)
            self.assertEqual("my_other_ref", self.so.client_order_ref)
            self.assertEqual("<p>my other note</p>", self.so.note)
