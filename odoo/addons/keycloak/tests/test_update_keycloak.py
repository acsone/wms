# Copyright 2021 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.addons.queue_job.tests.common import trap_jobs

from .common import TestKeycloak


class TestKeycloakUpdateFlow(TestKeycloak):
    def test_create(self):
        job_counter = self.job_counter()
        # when
        self.env["keycloak.user"].create(self.vals_user)
        # then
        queue_jobs = job_counter.search_created()
        self.assertTrue("create_user" in queue_jobs.func_string)  # implicitly 1 job

    def test_update_keycloak_user(self):
        user = self.env["keycloak.user"].create(self.vals_user)
        # when we write on the username, it does trigger an update
        with trap_jobs() as trap:
            user.username = "CoolerUsername33"
            trap.assert_jobs_count(1)
            trap.assert_enqueued_job(
                self.keycloak_backend.update_user_fields,
                args=(user, ["username"]),
                properties={"description": "Update Keycloak User CoolerUsername33"},
            )

        # when we write on the name, it triggers another update
        with trap_jobs() as trap:
            self.partner.name = "NewFirstname NewLastname"
            trap.assert_jobs_count(1)
            trap.assert_enqueued_job(
                self.keycloak_backend.update_user_fields,
                args=(user, ["name"]),
                properties={"description": "Update Keycloak User CoolerUsername33"},
            )

    def test_update_keycloak_partner(self):
        keycloak_user = self.env["keycloak.user"].create(self.vals_user)

        # if we write on the ref, it does not trigger an update
        with trap_jobs() as trap:
            self.partner.ref = "CustomerRef!"
            trap.assert_jobs_count(0)

        # when we write on the name, it does trigger an update
        with trap_jobs() as trap:
            self.partner.name = "NewFirstname NewLastname"
            trap.assert_jobs_count(1)
            trap.assert_enqueued_job(
                self.keycloak_backend.update_user_fields,
                args=(keycloak_user, ["name"]),
                properties={"description": "Update Keycloak User username"},
            )
        expected_payload = {"lastName": "NewLastname", "firstName": "NewFirstname"}
        payload = keycloak_user.keycloak_backend_id._get_user_payload(
            keycloak_user, ["name"]
        )
        self.assertEqual(payload, expected_payload)

    # @unittest.skip("Needs a running Keycloak backend.")
    def test_wizard(self):
        # the wizard works in no_delay, so we can't test it without a backend
        window_action = self.partner.action_create_keycloak_user()
        wizard = self.env["keycloak.partner.wizard"].browse(window_action["res_id"])
        wizard.password = "VeRyS4f3!"
        # when
        wizard.execute()
        # then: we created the keycloak user, we get the correct password
        self.assertEqual(wizard.password, self.partner.keycloak_user_ids.password)
