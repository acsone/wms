# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from contextlib import contextmanager

import mock

from odoo.tests.common import SavepointCase

from odoo.addons.base_rest.controllers.main import _PseudoCollection
from odoo.addons.component.core import WorkContext
from odoo.addons.component.tests.common import ComponentMixin


class TestPromoSubscriptions(SavepointCase, ComponentMixin):
    @classmethod
    def setUpClass(cls):
        super(TestPromoSubscriptions, cls).setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.setUpComponent()
        cls.product_1 = cls.env["product.product"].create(
            {
                "name": "product_1",
                "uom_id": cls.env.ref("product.product_uom_unit").id,
                "type": "product",
            }
        )
        cls.product_2 = cls.env["product.product"].create(
            {
                "name": "product_2",
                "uom_id": cls.env.ref("product.product_uom_unit").id,
                "type": "product",
            }
        )
        cls.partner_1 = cls.env["res.partner"].create({"name": "partner_1"})
        cls.partner_2 = cls.env["res.partner"].create({"name": "partner_2"})

    # pylint: disable=method-required-super
    def setUp(self):
        # resolve an inheritance issue (common.SavepointCase does not call
        # super)
        SavepointCase.setUp(self)
        ComponentMixin.setUp(self)

    @classmethod
    @contextmanager
    def promo_subscriptions_service(cls, authenticated_partner_id):
        env = cls.env(
            context=dict(
                cls.env.context, authenticated_partner_id=authenticated_partner_id
            )
        )
        collection = _PseudoCollection("shopinvader.backend", env)
        work = WorkContext(
            model_name="rest.service.registration",
            collection=collection,
            request=mock.Mock(),
            authenticated_partner_id=authenticated_partner_id,
        )
        yield work.component(usage="promo_subscriptions")

    def test_create(self):
        with self.promo_subscriptions_service(
            authenticated_partner_id=self.partner_1.id
        ) as service:
            result = service.create(product_id=self.product_1.id)
            self.assertDictEqual({"status": True}, result)

    def test_unlink(self):
        with self.promo_subscriptions_service(
            authenticated_partner_id=self.partner_1.id
        ) as service:
            result = service.create(product_id=self.product_1.id)
            self.assertDictEqual({"status": True}, result)
            result = service.get(self.product_1.id)
            self.assertTrue(result)
            service.delete(self.product_1.id)
            result = service.get(self.product_1.id)
            self.assertDictEqual({"status": False}, result)

    def test_acl(self):
        with self.promo_subscriptions_service(
            authenticated_partner_id=self.partner_1.id
        ) as service:
            service.create(product_id=self.product_1.id)
            result = service.search()
            self.assertTrue(result["data"])

        with self.promo_subscriptions_service(
            authenticated_partner_id=self.partner_2.id
        ) as service:
            result = service.get(self.product_1.id)
            self.assertDictEqual({"status": False}, result)
            result = service.search()
            self.assertFalse(result["data"])
