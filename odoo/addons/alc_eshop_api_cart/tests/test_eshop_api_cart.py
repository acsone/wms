# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from contextlib import contextmanager
from datetime import datetime

from freezegun import freeze_time

from odoo.exceptions import ValidationError

from .common import TestSaleCartRestApiInfoCase


class TestSaleCartRestApiInfo(TestSaleCartRestApiInfoCase):
    @contextmanager
    def _record_new_note_template(self, so):
        class _Result:
            new_mails = self.env["mail.mail"].browse()

        template = self.env.ref("alc_eshop_api_cart.sale_order_notify_note")
        subject = template._render_field("subject", so.ids)[so.id]
        domain = [("subject", "=", subject)]
        template.auto_delete = False
        all_mails = self.env["mail.mail"].search(domain)
        result = _Result()
        yield result
        result.new_mails = self.env["mail.mail"].search(domain) - all_mails

    def test_update(self):
        # ensure the api works when mixed with the native api
        with self._create_test_client() as test_client:
            response = test_client.post(
                "carts/info", json={"customer_ref": "my_ref", "note": "my note"}
            )
            self.assertEqual(200, response.status_code)
            self.assertEqual("my_ref", self.so.client_order_ref)
            self.assertEqual("<p>my note</p>", self.so.note)

            response = test_client.post(
                f"carts/{self.so.uuid}/info",
                json={"customer_ref": "my_other_ref", "note": "my other note"},
            )
            self.assertEqual(200, response.status_code)
            self.assertEqual("my_other_ref", self.so.client_order_ref)
            self.assertEqual("<p>my other note</p>", self.so.note)

    def test_confirm(self):
        date_order = datetime(2021, 1, 1, 7, 10, 0)
        self.so.date_order = date_order
        self.assertEqual(date_order, self.so.date_order)
        confirm_date = datetime(2021, 1, 1, 7, 20, 0)
        with freeze_time(confirm_date), self._create_test_client() as test_client:
            response = test_client.post(
                f"carts/{self.so.uuid}/confirm",
                json={"customer_ref": "my_ref", "note": "my note"},
            )

        self.assertEqual(200, response.status_code)
        info = response.json()

        self.assertEqual("sale", self.so.state)
        self.assertEqual("my_ref", self.so.client_order_ref)
        self.assertEqual("<p>my note</p>", self.so.note)
        self.assertTrue(info)
        self.assertIn(info["state"], ["processing", "sale"])
        self.assertEqual("my_ref", info["customer_ref"])
        self.assertEqual("<p>my note</p>", info["note"])
        self.assertEqual(confirm_date, self.so.date_order)

    def test_confirm_without_note_sent_mail(self):
        with self._record_new_note_template(
            self.so
        ) as result, self._create_test_client() as test_client:
            test_client.post(
                "carts/confirm",
                json={"uuid": self.so.uuid, "customer_ref": "my_ref", "note": ""},
            )
        new_mail = result.new_mails
        self.assertFalse(new_mail)

    def test_confirm_not_allowed(self):
        self.so.partner_id.eshop_ordering_allowed = False
        with self._create_test_client() as test_client:
            with self.assertRaises(ValidationError):
                test_client.post("carts/confirm", json={"uuid": self.so.uuid})

            self.so.partner_id.eshop_ordering_allowed = True
            response = test_client.post("carts/confirm", json={"uuid": self.so.uuid})
            self.assertEqual(200, response.status_code)
