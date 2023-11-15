# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.fastapi.tests.common import FastAPITransactionCase

from ..routers import promo_subscriptions_router


class TestPromoSubscriptions(FastAPITransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.default_fastapi_router = promo_subscriptions_router
        cls.product_1 = cls.env["product.product"].create(
            {
                "name": "product_1",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "type": "product",
            }
        )
        cls.product_2 = cls.env["product.product"].create(
            {
                "name": "product_2",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "type": "product",
            }
        )
        cls.partner_1 = cls.env["res.partner"].create({"name": "partner_1"})
        cls.partner_2 = cls.env["res.partner"].create({"name": "partner_2"})

    def test_create(self):
        with self._create_test_client(partner=self.partner_1) as client:
            response = client.post(
                "/promo_subscriptions",
                json={"product_id": self.product_1.id},
            )
            self.assertEqual(response.status_code, 200)
            self.assertDictEqual({"status": True}, response.json())

    def test_unlink(self):
        with self._create_test_client(partner=self.partner_1) as client:
            response = client.post(
                "/promo_subscriptions",
                json={"product_id": self.product_1.id},
            )
            self.assertEqual(response.status_code, 200)
            self.assertDictEqual({"status": True}, response.json())

            # check that the subscription exists
            response = client.get(f"/promo_subscriptions/{self.product_1.id}")
            self.assertEqual(response.status_code, 200)
            self.assertDictEqual({"status": True}, response.json())

            # unsubscribe
            response = client.delete(f"/promo_subscriptions/{self.product_1.id}")
            self.assertEqual(response.status_code, 204)

            # check that the subscription does not exist anymore
            response = client.get(f"/promo_subscriptions/{self.product_1.id}")
            self.assertEqual(response.status_code, 200)
            self.assertDictEqual({"status": False}, response.json())

    def test_acl(self):
        with self._create_test_client(partner=self.partner_1) as client:
            response = client.post(
                "/promo_subscriptions",
                json={"product_id": self.product_1.id},
            )
            self.assertEqual(response.status_code, 200)
            self.assertDictEqual({"status": True}, response.json())

            # get all subscriptions
            response = client.get("/promo_subscriptions")
            self.assertEqual(response.status_code, 200)
            self.assertDictEqual(
                {
                    "size": 1,
                    "data": [
                        {"product_id": self.product_1.id},
                    ],
                },
                response.json(),
            )

        with self._create_test_client(partner=self.partner_2) as client:
            # get all subscriptions
            response = client.get("/promo_subscriptions")
            self.assertEqual(response.status_code, 200)
            self.assertDictEqual(
                {
                    "size": 0,
                    "data": [],
                },
                response.json(),
            )

            # get status
            response = client.get(f"/promo_subscriptions/{self.product_1.id}")
            self.assertEqual(response.status_code, 200)
            self.assertDictEqual({"status": False}, response.json())
