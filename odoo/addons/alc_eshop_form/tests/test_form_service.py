# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from contextlib import contextmanager

import mock

from odoo.tests.common import SavepointCase

from odoo.addons.base_rest.controllers.main import _PseudoCollection
from odoo.addons.component.core import WorkContext
from odoo.addons.component.tests.common import ComponentMixin


class TestEShopForm(SavepointCase, ComponentMixin):
    @classmethod
    def setUpClass(cls):
        super(TestEShopForm, cls).setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.setUpComponent()
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
                "audience": "public_only",
                "email": "laurent.mignon@acsone.eu",
                "email_subject": "test subject",
                "form": "{}",
                "published": False,
            }
        )

    # pylint: disable=method-required-super
    def setUp(self):
        # resolve an inheritance issue (common.SavepointCase does not call
        # super)
        SavepointCase.setUp(self)
        ComponentMixin.setUp(self)

    @classmethod
    @contextmanager
    def form_service(cls, authenticated_partner_id):
        env = cls.env(
            context=dict(
                cls.env.context, authenticated_partner_id=authenticated_partner_id,
            )
        )
        collection = _PseudoCollection("shopinvader.backend", env)
        work = WorkContext(
            model_name="rest.service.registration",
            collection=collection,
            request=mock.Mock(),
            authenticated_partner_id=authenticated_partner_id,
        )
        yield work.component(usage="form")

    def test_search_public(self):
        with self.form_service(None) as service:
            res = service.dispatch("search")
        self.assertTrue(res)
        self.assertEqual(1, res.get("size"))
        self.assertEqual(self.form_public.id, res["data"][0]["id"])

    def test_search_published_only(self):
        with self.form_service(None) as service:
            res = service.dispatch("search")
        self.assertTrue(res)
        self.assertEqual(1, res.get("size"))
        self.assertEqual(self.form_public.id, res["data"][0]["id"])
        self.form_public_not_published.published = True
        with self.form_service(None) as service:
            res = service.dispatch("search")
        self.assertTrue(res)
        self.assertEqual(2, res.get("size"))

    def test_search_authenticated(self):
        with self.form_service(self.partner.id) as service:
            res = service.dispatch("search")
        self.assertTrue(res)
        self.assertEqual(1, res.get("size"))
        self.assertEqual(self.form_authenticated.id, res["data"][0]["id"])

    def test_submit(self):
        with self.form_service(self.partner.id) as service, mock.patch.object(
            self.EShopForm.__class__, "_send_collected_info"
        ) as mocked_send_info:
            res = service.dispatch(
                "submit",
                self.form_authenticated.id,
                params={"data": {"a": "a", "b": "b"}},
            )
            self.assertTrue(res)
            mocked_send_info.assert_called_once()
            mocked_send_info.assert_called_with({"a": "a", "b": "b"}, self.partner)
