# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from .common import TestRegistrationService


class TestRegistrationServiceFlow(TestRegistrationService):
    def test_creation__flow(self):
        params = self._get_registration_service_vals()
        with self._create_test_client() as test_client:
            response = test_client.post("/registrations", json=params)
            self.assertEqual(response.status_code, 202)
            result = response.json()
            self.assertTrue(result["id"])

            registration = self.env["alc.registration"].browse(result["id"])
            self.assertEqual(registration.occupation, "assistant")
            self.assertEqual(registration.country_name, "Belgik")
            title = self.env.ref("base.res_partner_title_doctor")
            self.assertEqual(registration.title, title)
            self.assertEqual(registration.vat, "vat")
            self.assertEqual(registration.clientele, "livestock,pet")

    def test_creation_veterinary(self):
        params = self._get_registration_service_vals()
        params["function"] = "function_veterinary"
        with self._create_test_client() as test_client:
            response = test_client.post("/registrations", json=params)
            self.assertEqual(response.status_code, 202)
            result = response.json()
            registration = self.env["alc.registration"].browse(result["id"])
            self.assertEqual(registration.occupation, "veterinary")
