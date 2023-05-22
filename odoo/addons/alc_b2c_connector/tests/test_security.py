# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from fastapi import status
from requests import Response

from odoo.exceptions import ValidationError
from odoo.tools.misc import mute_logger

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
                "is_b2c_customer": True,
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
        self.client.post(
            self._get_path("/sales/create"),
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
        response: Response = self.client.get(
            self._get_path("/sales/search"),
            headers={"api-key": "1234"},
            params={"ids": [2]},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        res = response.json()
        self.assertEqual(res["size"], 1)
        result = res["data"][0]
        self.assertEqual(result["customer_ref"], "Amazon_XYZ")
        # second client
        response: Response = self.client.get(
            self._get_path("/sales/search"),
            headers={"api-key": "5678"},
            params={"ids": [2]},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
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
        response: Response = self.client.get(
            self._get_path("/sales/search"),
            headers={"api-key": "1234"},
            params={"ids": [10]},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        res = response.json()
        self.assertEqual(res["size"], 1)
        # second client
        response: Response = self.client.get(
            self._get_path("/sales/search"),
            headers={"api-key": "5678"},
            params={"ids": [10]},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        res = response.json()
        self.assertEqual(res["size"], 0)

    @mute_logger("odoo.addons.alc_b2c_connector.models.res_partner")
    def test_02(self):
        """
        Test Case:

            call sale order service create with a partner of another client
        Expected Result:
            Access error
        """
        recipient_info = self._gen_recipent(_id="XYZ")
        params = {
            "id": 2,
            "customer_ref": self.vt_partner_2.ref,
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
        with self.assertRaises(
            ValidationError, msg="No match found for customer_id: Ebay_VTREF"
        ):
            self.sale_model._create_from_b2c(params, self.b2c_client)

    def test_03(self):
        """Each client can access to his partners."""
        # first client
        response: Response = self.client.get(
            self._get_path("/recipients/VTREF"), headers={"api-key": "1234"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        res = response.json()
        self.assertEqual(res["name"], "VT")
        # second client
        response: Response = self.client.get(
            self._get_path("/recipients/VTREF"), headers={"api-key": "5678"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        res = response.json()
        self.assertEqual(res["name"], "VT 2")
