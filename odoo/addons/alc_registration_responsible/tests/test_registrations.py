# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.addons.alc_registration.tests.common import TestRegistration


class TestRegistrationFlow(TestRegistration):
    def test_creation_flow(self):
        vals = self._get_registration_vals()

        registration = self.model.create(vals)

        domain_message = [("model", "=", "alc.registration")]
        message = self.env["mail.message"].search(domain_message)
        self.assertTrue(registration.name in message.subject)
