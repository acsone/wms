# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestResPartner(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestResPartner, cls).setUpClass()
        cls.ResPartner = cls.env["res.partner"]
        cls.bc2_category = cls.env.ref(
            "alc_b2c_partner.res_partner_category_b2c_customer"
        )
        cls.partner = cls.ResPartner.create({"name": "my test partner"})

    def test_00(self):
        """
        Data:
            partner without category
        Test case:
            set is_bc2_customer
            unset is_b2c_customer
        Expected result
            b2c category must be set on the partner
            b2c category must be removed from the partner
        """
        self.assertFalse(self.partner.category_id)
        self.partner.is_b2c_customer = True
        self.assertEqual(self.partner.category_id, self.bc2_category)
        self.partner.is_b2c_customer = False
        self.assertFalse(self.partner.category_id)

    def test_01(self):
        """
        Data:
            partner without category
        Test case:
            add b2c_category
            remove b2c_category
        Expected result
            is_b2c_customer is True
            is_b2c_customer is False
        """
        self.assertFalse(self.partner.is_b2c_customer)
        self.partner.write({"category_id": [(4, self.bc2_category.id)]})
        self.assertTrue(self.partner.is_b2c_customer)
        self.partner.write({"category_id": [(3, self.bc2_category.id)]})
        self.assertFalse(self.partner.is_b2c_customer)
