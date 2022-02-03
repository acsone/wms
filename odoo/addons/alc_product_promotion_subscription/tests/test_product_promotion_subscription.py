# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError
from odoo.tests.common import SavepointCase


class TestPromoSubscriptions(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestPromoSubscriptions, cls).setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
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
        cls.parther_1 = cls.env["res.partner"].create({"name": "partner_1"})
        cls.PromoSubscription = cls.env["alc.product.promotion.subscription"]

    def test_subscribe(self):
        res = self.PromoSubscription.subscribe(self.parther_1, self.product_1)
        self.assertTrue(res)
        with self.assertRaises(UserError), self.env.cr.savepoint():
            self.PromoSubscription.subscribe(self.parther_1, self.product_1)
        res = self.PromoSubscription.subscribe(self.parther_1, self.product_2)
        self.assertTrue(res)
        res = self.PromoSubscription.search([("partner_id", "=", self.parther_1.id)])
        self.assertEqual(2, len(res))

    def test_unsubscribe(self):
        self.PromoSubscription.subscribe(self.parther_1, self.product_1)
        res = self.PromoSubscription.search([("partner_id", "=", self.parther_1.id)])
        self.assertEqual(1, len(res))
        self.PromoSubscription.unsubscribe(self.parther_1, self.product_1)
        res = self.PromoSubscription.search([("partner_id", "=", self.parther_1.id)])
        self.assertFalse(res)

    def test_active(self):
        res = self.PromoSubscription.subscribe(self.parther_1, self.product_1)
        self.assertTrue(res.active)
        self.product_1.active = False
        self.assertFalse(res.active)
        self.product_1.active = True
        self.assertTrue(res.active)
        self.parther_1.active = False
        self.assertFalse(res.active)
        self.parther_1.active = True
        self.assertTrue(res.active)
