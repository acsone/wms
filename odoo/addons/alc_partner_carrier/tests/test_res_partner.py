# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests.common import SavepointCase


class TestResPartner(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestResPartner, cls).setUpClass()
        cls.ResPartner = cls.env["res.partner"]
        cls.carrier_category = cls.env.ref(
            "alc_partner_carrier.res_partner_category_carrier"
        )
        cls.partner = cls.ResPartner.create({"name": "my test partner"})

    def test_00(self):
        """
        Data:
            partner without category
        Test case:
            set is_carrier
            unset is_carrier
        Expected result
            carrier category must be set on the partner
            carrier category must be removed from the partner
        """
        self.assertFalse(self.partner.category_id)
        self.partner.is_carrier = True
        self.assertEqual(self.partner.category_id, self.carrier_category)
        self.partner.is_carrier = False
        self.assertFalse(self.partner.category_id)

    def test_01(self):
        """
        Data:
            partner without category
        Test case:
            add carrier_category
            remove carrier_category
        Expected result
            is_carrier is True
            is_carrier is False
        """
        self.assertFalse(self.partner.is_carrier)
        self.partner.write({"category_id": [(4, self.carrier_category.id)]})
        self.assertTrue(self.partner.is_carrier)
        self.partner.write({"category_id": [(3, self.carrier_category.id)]})
        self.assertFalse(self.partner.is_carrier)
