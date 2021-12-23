# coding: utf-8
# Copyright 2021 ACSONE SA/NV.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from .common import TestESRoles


class TestESRolesFlow(TestESRoles):
    def test_default_partner_role(self):
        # given
        vals_partner = {"name": "P"}
        # when
        partner = self.env["res.partner"].create(vals_partner)
        # then
        self.assertTrue("guest" in partner.elasticsearch_role)
        self.assertTrue(partner.partner_type in partner.elasticsearch_role)
        price_role_name = partner.property_product_pricelist.role_name
        self.assertTrue(price_role_name in partner.elasticsearch_role)

    def test_partner_role(self):
        # given
        vals_partner = {"name": "P", "partner_type": "guest"}
        partner = self.env["res.partner"].create(vals_partner)
        # when
        partner.property_product_pricelist = self.pricelist
        # then
        expected1 = "price-bons-prixs,guest"
        expected2 = "guest,price-bons-prixs"
        self.assertTrue(partner.elasticsearch_role in (expected1, expected2))
