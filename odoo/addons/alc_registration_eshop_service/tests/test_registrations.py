# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from .common import TestRegistrationService


class TestRegistrationServiceFlow(TestRegistrationService):
    def test_creation__flow(self):
        params = self._get_registration_service_vals()
        with self.registrations_service() as service:
            result = service.dispatch("submit", params=params)
            self.assertTrue(result["id"])
