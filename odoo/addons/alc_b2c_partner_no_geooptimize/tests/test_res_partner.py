# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestResPartner(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ResPartner = cls.env["res.partner"]
        cls.bc2_category = cls.env.ref(
            "alc_b2c_partner.res_partner_category_b2c_customer"
        )
        cls.partner = cls.ResPartner.create({"name": "my test partner"})

    def test_00(self):
        """
        Data:

            partner without is_bc2_customer and without in_geo_release_channel
        Test case:
            set is_bc2_customer
            unset is_b2c_customer
        Expected result
            in_geo_release_channel is true
            in_geo_release_channel is unchanged
        """
        self.assertFalse(self.partner.is_b2c_customer)
        self.assertTrue(self.partner.in_geo_release_channel)
        self.partner.is_b2c_customer = True
        self.assertFalse(self.partner.in_geo_release_channel)
        self.partner.is_b2c_customer = False
        self.assertFalse(self.partner.in_geo_release_channel)

    def test_01(self):
        """
        Data:

            partner without category
        Test case:
            add b2c_category
            remove b2c_category
        Expected result
            in_geo_release_channel is true
            in_geo_release_channel is unchanged
        """
        self.assertTrue(self.partner.in_geo_release_channel)
        self.partner.write({"category_id": [(4, self.bc2_category.id)]})
        self.assertFalse(self.partner.in_geo_release_channel)
        self.partner.write({"category_id": [(3, self.bc2_category.id)]})
        self.assertFalse(self.partner.in_geo_release_channel)
