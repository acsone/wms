# Copyright 2021 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.addons.queue_job.tests.common import trap_jobs

from .common import TestKeycloak


class TestKeycloakUpdateFlow(TestKeycloak):
    def test_create(self):
        with trap_jobs() as trap:
            keycloak_user = self.env["keycloak.user"].create(self.vals_user)
            trap.assert_jobs_count(1)
            trap.assert_enqueued_job(
                self.keycloak_backend.create_user, args=(keycloak_user,)
            )

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

    def test_wizard(self):
        # the wizard works in no_delay, so we can't test it without a backend
        self.assertFalse(self.partner.keycloak_user_ids)
        window_action = self.partner.action_create_keycloak_user()
        wizard = self.env["keycloak.partner.wizard"].browse(window_action["res_id"])
        wizard.password = "VeRyS4f3!"
        # when
        wizard.execute()
        # then: we created the keycloak user, we get the correct password
        self.assertTrue(self.partner.keycloak_user_ids)
        self.assertTrue(self.partner.keycloak_user_ids.keycloak_id)
        with trap_jobs() as trap:
            keycloak_user = self.partner.keycloak_user_ids
            keycloak_user.partner_id.email = "test@test.com"
            trap.assert_enqueued_job(
                self.keycloak_backend.update_user_fields,
                args=(keycloak_user, ["email"]),
            )
            trap.perform_enqueued_jobs()
        with trap_jobs() as trap:
            keycloak_id = keycloak_user.keycloak_id
            keycloak_user.unlink()
            trap.assert_enqueued_job(
                self.keycloak_backend.delete_user, args=(keycloak_id,)
            )
            trap.perform_enqueued_jobs()
