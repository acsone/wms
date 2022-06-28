# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from .common import TestRegistration


class TestRegistrationFlow(TestRegistration):
    def test_creation_flow(self):
        vals = self._get_registration_vals()

        registration = self.model.create(vals)

        self.assertEqual(registration.state, "pending")
        self.assertEqual(registration.clientele, "equine")

        partner = registration.create_partners()

        self.assertEqual(registration.state, "accepted")
        self.assertEqual(registration.name, partner.name)
        self.assertEqual(registration.partner_id, partner)

        # the partner already exist, do nothing
        no_partner = registration.create_partners()

        self.assertFalse(no_partner)
        self.assertEqual(registration.state, "accepted")

    def test_archive(self):
        vals = self._get_registration_vals()
        registration = self.model.create(vals)

        registration.action_archive()
        self.assertEqual(registration.state, "rejected")

        registration.action_reset_to_pending()
        self.assertEqual(registration.state, "pending")
