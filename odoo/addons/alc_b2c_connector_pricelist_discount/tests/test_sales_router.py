# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from fastapi import status
from freezegun import freeze_time
from requests import Response

from odoo import fields

from odoo.addons.alc_b2c_connector.routers.sales import router as sales_router
from odoo.addons.alc_b2c_connector.tests.common import CommonB2CSaleServiceCase

ISO_DT_WITH_TZ = "2020-05-28T13:45:47+02:00"


class TestSalesService(CommonB2CSaleServiceCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.default_fastapi_router = sales_router
        # create a b2c_partner
        cls.discount_pricelist_id = cls.env.ref(
            "alc_b2c_connector.product_pricelist_b2c"
        )
        cls.discount_pricelist_id.currency_id = cls.currency_id
        cls.b2c_client.discount_pricelist_id = cls.discount_pricelist_id

    @freeze_time("2020-05-28 11:45:47")
    def test_01(self):
        """
        Data:

            An existing veterinary
        Test case:
            Create a new SO for a new partner and the existing veterinary
        Expected result:
            A new partner is created
            A new SO is created with:
                partner -> new partner
                shipping partner -> the veterinary
                invoice partner -> the veterinary
                priclist -> the one from the backend
                payment_mode -> the one from the backend
                payment_term_id -> the one from the backend
                supplier_promotion_allowed -> the one from the veterinary
        """
        recipient_info = self._gen_recipent()
        params = {
            "id": 2,
            "customer_ref": self.vt_partner.ref,
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
        with self._create_test_client() as client:
            response: Response = client.post(
                "/sales/create",
                headers={"api-key": "1234"},
                json=params,
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        res = response.json()
        self.assertTrue(res)
        new_so = self._get_so_from_name(res["ref"])
        self.assertTrue(new_so)
        self.assertEqual(
            new_so.partner_id.ref,
            f"{self.b2c_client.sale_channel_id.code}_{recipient_info['id']}",
        )
        self.assertEqual(new_so.partner_invoice_id, self.vt_partner)
        self.assertEqual(new_so.partner_shipping_id, self.vt_partner)
        self.assertEqual(new_so.partner_id.sale_reason_backorder_strategy, "cancel")
        self.assertEqual(
            new_so.date_order, fields.Datetime.to_datetime("2020-05-28 11:45:47")
        )
        self.assertTrue(self.b2c_client.pricelist_id)
        self.assertEqual(new_so.pricelist_id, self.b2c_client.pricelist_id)
        self.assertTrue(self.b2c_client.sale_team_id)
        self.assertEqual(new_so.team_id, self.b2c_client.sale_team_id)
        self.assertTrue(self.b2c_client.payment_mode_id)
        self.assertEqual(new_so.payment_mode_id, self.b2c_client.payment_mode_id)
        self.assertEqual(self.b2c_client.payment_term_id, self.payment_term_test)
        self.assertEqual(new_so.payment_term_id, self.payment_term_test)
        self.assertTrue(new_so.supplier_promotion_allowed)
        self.assertEqual(1, len(new_so.order_line))
        sol = new_so.order_line
        self.assertEqual(sol.product_id, self.saleable_product)
        self.assertEqual(sol.discount3, 12)  # discount in %
        self.assertEqual(sol.price_unit, 10)
        self.assertEqual(sol.product_qty, 10)
