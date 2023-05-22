# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestPromoSubscriptions(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_1 = cls.env["product.product"].create(
            {"name": "product_1", "type": "product"}
        )
        cls.product_2 = cls.env["product.product"].create(
            {"name": "product_2", "type": "product"}
        )
        cls.partner_1 = cls.env["res.partner"].create({"name": "partner_1"})
        cls.PromoSubscription = cls.env["alc.product.promotion.subscription"]

    def test_subscribe(self):
        res = self.PromoSubscription.subscribe(self.partner_1, self.product_1)
        self.assertTrue(res)
        with self.assertRaises(UserError), self.env.cr.savepoint():
            self.PromoSubscription.subscribe(self.partner_1, self.product_1)
        res = self.PromoSubscription.subscribe(self.partner_1, self.product_2)
        self.assertTrue(res)
        res = self.PromoSubscription.search([("partner_id", "=", self.partner_1.id)])
        self.assertEqual(2, len(res))

    def test_unsubscribe(self):
        self.PromoSubscription.subscribe(self.partner_1, self.product_1)
        res = self.PromoSubscription.search([("partner_id", "=", self.partner_1.id)])
        self.assertEqual(1, len(res))
        self.PromoSubscription.unsubscribe(self.partner_1, self.product_1)
        res = self.PromoSubscription.search([("partner_id", "=", self.partner_1.id)])
        self.assertFalse(res)

    def test_active(self):
        res = self.PromoSubscription.subscribe(self.partner_1, self.product_1)
        self.assertTrue(res.active)
        self.product_1.active = False
        self.assertFalse(res.active)
        self.product_1.active = True
        self.assertTrue(res.active)
        self.partner_1.active = False
        self.assertFalse(res.active)
        self.partner_1.active = True
        self.assertTrue(res.active)
