# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.alc_elasticsearch_security.tests.common import TestESRoles


class TestESRolesLoyalty(TestESRoles):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.loyalty_program = cls.env["loyalty.program"].create(
            {"name": "Bons de fidélité"}
        )
        cls.partner = cls.env["res.partner"].create({"name": "Test"})

    def test_no_role_for_public_program(self):
        self.assertTrue(self.loyalty_program.is_public)
        self.assertNotIn(
            self.loyalty_program._get_role_name(), self.partner.elasticsearch_role
        )

    def test_role_for_private_program(self):
        self.loyalty_program.partner_ids = self.partner
        self.assertIn(
            self.loyalty_program._get_role_name(), self.partner.elasticsearch_role
        )
