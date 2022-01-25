# Copyright 2021 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import unittest

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
        job_counter = self.job_counter()

        # if we write on the password, it does not trigger an update
        user.password = "VeRyS4f3!"
        # then
        queue_jobs = job_counter.search_created()
        self.assertEqual(len(queue_jobs), 0)

        # when we write on the username, it does trigger an update
        user.username = "CoolerUsername33"
        # then
        queue_job = job_counter.search_created()
        self.assertTrue("Update" in queue_job.name)

        # when we write again the username,
        user.username = "CoolestUsername333"
        # then it does not trigger an update: identity_key on the job
        self.assertEqual(len(job_counter.search_created()), 1)

    def test_update_keycloak_partner(self):
        keycloak_user = self.env["keycloak.user"].create(self.vals_user)
        job_counter = self.job_counter()

        # if we write on the ref, it does not trigger an update
        self.partner.ref = "CustomerRef!"
        # then
        queue_jobs = job_counter.search_created()
        self.assertEqual(len(queue_jobs), 0)

        # when we write on the name, it does trigger an update
        self.partner.name = "NewFirstname NewLastname"
        # then
        queue_job = job_counter.search_created()
        self.assertTrue("Update" in queue_job.name)
        expected_payload = {"lastName": "NewLastname", "firstName": "NewFirstname"}
        payload = keycloak_user.keycloak_backend_id._get_user_payload(*queue_job.args)
        self.assertEqual(payload, expected_payload)

    @unittest.skip("Needs a running Keycloak backend.")
    def test_wizard(self):
        # the wizard works in no_delay, so we can't test it without a backend
        window_action = self.partner.action_create_keycloak_user()
        wizard = self.env["keycloak.partner.wizard"].browse(window_action["res_id"])
        wizard.password = "VeRyS4f3!"
        # when
        wizard.execute()
        # then: we created the keycloak user, we get the correct password
        self.assertEqual(wizard.password, self.partner.keycloak_user_ids.password)
