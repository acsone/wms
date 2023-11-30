# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from fastapi import status
from requests import Response

from ..routers.recipients import router as recipients_router
from ..routers.sales import router as sales_router
from .common import CommonB2CSaleServiceCase

ISO_DT_WITH_TZ = "2020-05-28T13:45:47+02:00"


class TestSaleOrder(CommonB2CSaleServiceCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.sale_channel_2 = cls.env.ref("sale_channel.sale_channel_ebay")
        cls.b2c_client_2 = cls.env["alc.b2c.client"].create(
            {
                "name": "B2c backend test 2",
                "product_assortment_id": cls.env.ref(
                    "alc_b2c_connector.b2c_product_assortment_filter"
                ).id,
                "pricelist_id": cls.pricelist_id.id,
                "sale_team_id": cls.env.ref("sales_team.salesteam_website_sales").id,
                "payment_mode_id": cls.payment_mode.id,
                "sale_channel_id": cls.sale_channel_2.id,
                "sale_reason_backorder_strategy": "cancel",
                "api_key": "5678",
                "partner_id": cls.b2c_user.partner_id.id,
                "fastapi_endpoint_id": cls.endpoint.id,
            }
        )
        cls.sale_model = (
            cls.env["sale.order"]
            .with_user(cls.b2c_user)
            .with_context(alc_b2c_client_id=cls.b2c_client.id)
        )
        cls.vt_partner_2 = cls.env["res.partner"].create(
            {
                "name": "VT 2",
                "partner_type": "veterinary",
                "ref": f"{cls.sale_channel_2.name}_VTREF",
                "email": "vt@vt.be",
                "supplier_promotion_sale_allowed": True,
                "customer_payment_mode_id": cls.vt_payment_mode.id,
            }
        )
        cls.b2c_partner_2 = cls.env["res.partner"].create(
            {
                "name": "EXISTING B2C PARTNER 2",
                "is_b2c_customer": True,
                "partner_type": "student_like",
                "ref": f"{cls.sale_channel_2.name}_ABC",
                "email": "b2c@b2c.be",
                "alc_b2c_client_id": cls.b2c_client_2.id,
            }
        )

    def _create_sale_order(self, b2c_client, vt_partner):
        recipient_info = self._gen_recipent(_id="XYZ")
        params = {
            "id": 2,
            "customer_ref": vt_partner.ref,
            "date": ISO_DT_WITH_TZ,
            "recipient": recipient_info,
            "lines": [
                {
                    "line_id": 2,
                    "sku": self.saleable_product.default_code,
                    "quantity": 10,
                }
            ],
        }
        with self._create_test_client(router=sales_router) as client:
            client.post(
                "/sales/create",
                headers={"api-key": b2c_client.api_key},
                json=params,
            )

    def test_00(self):
        """
        Test Case:

            Create two sale orders from different clients
        Expected Result:
            Each client can access only to his sale order
        """
        self._create_sale_order(self.b2c_client, self.vt_partner)
        order = self.env["sale.order"].search(
            [("b2c_ref", "=", "2"), ("alc_b2c_client_id", "=", self.b2c_client.id)]
        )
        self.assertTrue(order)
        self.assertEqual(order.alc_b2c_client_id, self.b2c_client)
        self._create_sale_order(self.b2c_client_2, self.vt_partner_2)
        order = self.env["sale.order"].search(
            [("b2c_ref", "=", "2"), ("alc_b2c_client_id", "=", self.b2c_client_2.id)]
        )
        self.assertTrue(order)
        self.assertEqual(order.alc_b2c_client_id, self.b2c_client_2)
        self.assertEqual(len(self.env["sale.order"].search([("b2c_ref", "=", "2")])), 2)
        # first client
        with self._create_test_client(router=sales_router) as client:
            response: Response = client.get(
                "/sales/search",
                headers={"api-key": "1234"},
                params={"ids[]": [2]},
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())
        res = response.json()
        self.assertEqual(res["size"], 1)
        result = res["data"][0]
        self.assertEqual(result["customer_ref"], "Amazon_XYZ")
        # second client
        with self._create_test_client(router=sales_router) as client:
            response: Response = client.get(
                "/sales/search",
                headers={"api-key": "5678"},
                params={"ids[]": [2]},
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())
        res = response.json()
        self.assertEqual(res["size"], 1)
        result = res["data"][0]
        self.assertEqual(result["customer_ref"], "Ebay_XYZ")

    def test_01(self):
        """
        Test Case:

            call sale order service get for an order of another client
        Expected Result:
            Each client can access only to his sale order
        """
        # first client
        with self._create_test_client(router=sales_router) as client:
            response: Response = client.get(
                "/sales/search",
                headers={"api-key": "1234"},
                params={"ids[]": [10]},
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())
        res = response.json()
        self.assertEqual(res["size"], 1)
        # second client
        with self._create_test_client(router=sales_router) as client:
            response: Response = client.get(
                "/sales/search",
                headers={"api-key": "5678"},
                params={"ids[]": [10]},
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())
        res = response.json()
        self.assertEqual(res["size"], 0)

    def test_02(self):
        """Each client can access to his partners."""
        # first client
        with self._create_test_client(router=recipients_router) as client:
            response: Response = client.get(
                "/recipients/ABC", headers={"api-key": "1234"}
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())
        res = response.json()
        self.assertEqual(res["name"], "EXISTING B2C PARTNER")
        # second client
        with self._create_test_client(router=recipients_router) as client:
            response: Response = client.get(
                "/recipients/ABC", headers={"api-key": "5678"}
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())
        res = response.json()
        self.assertEqual(res["name"], "EXISTING B2C PARTNER 2")
