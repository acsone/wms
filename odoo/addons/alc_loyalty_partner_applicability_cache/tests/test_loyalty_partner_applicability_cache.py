# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.loyalty_partner_applicability.tests.common import (
    TestLoyaltyPartnerApplicabilityCase,
)


class TestLoyaltyPartner_ApplicabilityCache(TestLoyaltyPartnerApplicabilityCase):

    def test_update_program_update_cache(self):
        # partner2 is intot the domain of program_restricted_to_partner_domain
        program = self.program_restricted_to_partner_domain
        self.assertIn(self.partner2, program.all_restricted_partner_ids)
        program.write({"active": False})
        self.assertNotIn(self.partner2, program.all_restricted_partner_ids)
        program.write({"active": True})
        self.assertIn(self.partner2, program.all_restricted_partner_ids)

    def test_update_partner_update_cache(self):
        # partner2 is intot the domain of program_restricted_to_partner_domain
        program = self.program_restricted_to_partner_domain
        program.partner_domain = "[('active', '=', True)]"
        self.assertIn(self.partner2, program.all_restricted_partner_ids)
        self.partner2.active = False
        self.assertNotIn(self.partner2, program.all_restricted_partner_ids)
        self.partner2.active = True
        new_partner = self.env["res.partner"].create({"name": "Test"})
        self.assertTrue(new_partner.active)
        self.assertIn(new_partner, program.all_restricted_partner_ids)
        self.assertIn(program, new_partner.restricted_loyalty_program_ids)

    def test_set_partner_ids_update_cache(self):
        # partner2 is intot the domain of program_restricted_to_partner_domain
        program = self.program_no_restriction
        self.assertNotIn(self.partner2, program.all_restricted_partner_ids)
        program.partner_ids = self.partner2
        self.assertIn(self.partner2, program.all_restricted_partner_ids)
        program.partner_ids = False
        self.assertNotIn(self.partner2, program.all_restricted_partner_ids)
