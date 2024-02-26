# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from collections.abc import Callable
from typing import Any

from fastapi import APIRouter, FastAPI

from odoo.api import Environment

from odoo.addons.base.models.res_partner import Partner
from odoo.addons.base.models.res_users import Users
from odoo.addons.extendable_fastapi.tests.common import FastAPITransactionCase
from odoo.addons.shopinvader_api_cart.routers import cart

from ..routers import carts_router


class TestSaleCartApi(FastAPITransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
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
        vals_product = {"name": "N", "default_code": "sku"}
        cls.product_sku_n = cls.env["product.product"].create(vals_product)
        cls.stock_location = cls.env.ref("stock.stock_location_stock")

    def _create_test_client(
        self,
        app: FastAPI | None = None,
        router: APIRouter | None = None,
        user: Users | None = None,
        partner: Partner | None = None,
        env: Environment = None,
        dependency_overrides: dict[Callable[..., Any], Callable[..., Any]] = None,
        raise_server_exceptions: bool = True,
    ):
        if not app:
            app = FastAPI()
            app.include_router(carts_router)
            app.include_router(cart.cart_router, prefix="/carts")
        return super()._create_test_client(
            app=app,
            router=router,
            user=user,
            partner=partner,
            env=env,
            dependency_overrides=dependency_overrides,
            raise_server_exceptions=raise_server_exceptions,
        )

    @classmethod
    def _define_product_qty(cls, product, qty, location=None):
        location = location or cls.env.ref("stock.stock_location_stock")
        cls.env["stock.quant"].with_context(inventory_mode=True).create(
            {
                "product_id": product.id,
                "inventory_quantity": qty,
                "location_id": location.id,
            }
        ).action_apply_inventory()

    def test_qty_unavailable(self):
        with self._create_test_client() as test_client:
            response = test_client.get("/carts")
            self.assertEqual(200, response.status_code)

            # not product in stock
            self.assertEqual(self.so.order_line.product_qty_unavailable, 1.0)

            # add product in stock
            self._define_product_qty(self.product_1, 10)

            response = test_client.post("/carts/refresh_qty_unavailable")
            self.assertEqual(200, response.status_code)
            info = response.json()
            self.assertEqual(self.so.order_line.product_qty_unavailable, 0)
            self.assertEqual(-1.0, info["lines"][0]["qty_unavailable_diff"])
