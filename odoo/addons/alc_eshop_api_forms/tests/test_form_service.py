# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from unittest import mock

from odoo.addons.fastapi.tests.common import FastAPITransactionCase

from ..routers import forms_router


class TestEShopForm(FastAPITransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.default_fastapi_router = forms_router
        cls.partner = cls.env["res.partner"].create({"name": "partner"})
        cls.EShopForm = cls.env["alc.eshop.form"]
        cls.EShopForm.search([]).unlink()
        cls.form_authenticated = cls.EShopForm.create(
            {
                "name": "test form authenticated",
                "audience": "authenticated_only",
                "email": "laurent.mignon@acsone.eu",
                "email_subject": "test subject",
                "form": "{}",
                "published": True,
            }
        )
        cls.form_public = cls.EShopForm.create(
            {
                "name": "test form public",
                "audience": "public_only",
                "email": "laurent.mignon@acsone.eu",
                "email_subject": "test subject",
                "form": "{}",
                "published": True,
            }
        )
        cls.form_public_not_published = cls.EShopForm.create(
            {
                "name": "test form public",
                "code": "UNP_PUB",
                "audience": "public_only",
                "email": "laurent.mignon@acsone.eu",
                "email_subject": "test subject",
                "form": "{}",
                "published": False,
            }
        )

    def test_search_public(self):
        with self._create_test_client(partner=None) as test_client:
            response = test_client.get("/forms")
        self.assertEqual(200, response.status_code)
        res = response.json()
        self.assertEqual(1, res.get("size"))
        self.assertEqual(self.form_public.id, res["data"][0]["id"])

    def test_search_published_only(self):
        with self._create_test_client(partner=None) as test_client:
            response = test_client.get("/forms")
        self.assertEqual(200, response.status_code)
        res = response.json()
        self.assertTrue(res)
        self.assertEqual(1, res.get("size"))
        self.assertEqual(self.form_public.id, res["data"][0]["id"])
        self.form_public_not_published.published = True
        with self._create_test_client(partner=None) as test_client:
            response = test_client.get("/forms")
        self.assertEqual(200, response.status_code)
        res = response.json()
        self.assertTrue(res)
        self.assertEqual(2, res.get("size"))

    def test_search_authenticated(self):
        with self._create_test_client(partner=self.partner) as test_client:
            response = test_client.get("/forms")
        self.assertEqual(200, response.status_code)
        res = response.json()
        self.assertTrue(res)
        self.assertEqual(1, res.get("size"))
        self.assertEqual(self.form_authenticated.id, res["data"][0]["id"])

    def test_submit(self):
        with self._create_test_client(
            partner=self.partner
        ) as test_client, mock.patch.object(
            self.EShopForm.__class__, "_send_collected_info"
        ) as mocked_send_info:
            response = test_client.post(
                f"/forms/{self.form_authenticated.id}",
                json={"data": {"a": "a", "b": "b"}},
            )
            self.assertEqual(200, response.status_code)
            res = response.json()
            self.assertTrue(res)
            mocked_send_info.assert_called_once()
            mocked_send_info.assert_called_with({"a": "a", "b": "b"}, self.partner)
