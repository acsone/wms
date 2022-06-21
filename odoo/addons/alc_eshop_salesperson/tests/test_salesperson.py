# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.sale_cart_rest_api.tests.common import TestSaleCartRestApiCase


class TestSalesperson(TestSaleCartRestApiCase):
    @classmethod
    def setUpClass(cls):
        super(TestSalesperson, cls).setUpClass()
        cls.eshop_salesperson = cls.env.ref("alc_eshop_salesperson.eshop_salesperson")

    def test_new_cart(self):
        with self.cart_service(self.public_partner.id) as service:
            new_cart = service._create_empty_cart()
            self.assertEqual(new_cart.user_id, self.eshop_salesperson)
