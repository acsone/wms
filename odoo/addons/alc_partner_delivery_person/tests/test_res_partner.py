# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestResPartner(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestResPartner, cls).setUpClass()
        cls.ResPartner = cls.env["res.partner"]
        cls.delivery_person_category = cls.env.ref(
            "alc_partner_delivery_person.res_partner_category_delivery_person"
        )
        cls.partner = cls.ResPartner.create({"name": "my test partner"})

    def test_00(self):
        """
        Data:
            partner without category
        Test case:
            set is_delivery_person
            unset is_delivery_person
        Expected result
            delivery_person category must be set on the partner
            delivery_person category must be removed from the partner
        """
        self.assertFalse(self.partner.category_id)
        self.partner.is_delivery_person = True
        self.assertEqual(self.partner.category_id, self.delivery_person_category)
        self.partner.is_delivery_person = False
        self.assertFalse(self.partner.category_id)

    def test_01(self):
        """
        Data:
            partner without category
        Test case:
            add delivery_person_category
            remove delivery_person_category
        Expected result
            is_delivery_person is True
            is_delivery_person is False
        """
        self.assertFalse(self.partner.is_delivery_person)
        self.partner.write({"category_id": [(4, self.delivery_person_category.id)]})
        self.assertTrue(self.partner.is_delivery_person)
        self.partner.write({"category_id": [(3, self.delivery_person_category.id)]})
        self.assertFalse(self.partner.is_delivery_person)
