# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from fastapi import status
from requests import Response

from odoo.addons.extendable_fastapi.tests.common import FastAPITransactionCase
from odoo.addons.shopinvader_api_sale.routers import sale_router


class TestSale(FastAPITransactionCase):

    # TODO following code and access right must be shared between cart and sale
    # Maybe all the sale endpoint should be done in the shopinvader_api_cart ?
    # maybe we should named it "shopinvader_api_sale"
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        partner = cls.env["res.partner"].create({"name": "FastAPI Cart Demo"})

        cls.default_fastapi_authenticated_partner = partner
        cls.default_fastapi_router = sale_router
        cls.normal_sale_order = cls.env["sale.order"].create(
            {"partner_id": cls.default_fastapi_authenticated_partner.id}
        )
        cls.blanket_sale_order = cls.env["sale.order"].create(
            {
                "partner_id": cls.default_fastapi_authenticated_partner.id,
                "order_type": "blanket",
                "blanket_validity_end_date": "2023-01-01",
                "blanket_validity_start_date": "2022-01-01",
            }
        )
        # if sale_channel is installed
        channel_id = cls.env.ref(
            "alc_sale_channel.sale_channel_web", raise_if_not_found=False
        )
        if channel_id:
            cls.normal_sale_order.write({"sale_channel_id": channel_id.id})
            cls.blanket_sale_order.write({"sale_channel_id": channel_id.id})

    def test_search_sales(self):
        with self._create_test_client(router=sale_router) as test_client:
            response: Response = test_client.get("/sales")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["count"], 1)
        self.assertEqual(response.json()["items"][0]["id"], self.normal_sale_order.id)

    def test_get_sale(self):
        with self._create_test_client(router=sale_router) as test_client:
            response: Response = test_client.get(f"/sales/{self.normal_sale_order.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["id"], self.normal_sale_order.id)

        with self._create_test_client(
            router=sale_router, raise_server_exceptions=False
        ) as test_client:
            response: Response = test_client.get(f"/sales/{self.blanket_sale_order.id}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
