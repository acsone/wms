# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestSalesPerson(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test partner"})

    def test_create(self):
        cart = self.env["sale.order"]._create_empty_cart(self.partner.id)
        self.assertEqual(
            cart.user_id,
            self.env.ref("alc_eshop_sale_cart_salesperson.eshop_salesperson"),
        )
