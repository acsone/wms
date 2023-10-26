# Copyright 2021 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import TransactionCase

from odoo.addons.queue_job.tests.common import JobMixin


class TestKeycloak(TransactionCase, JobMixin):
    @classmethod
    def setUpClass(cls):
        # Note that adding TEST_QUEUE_JOB_NO_DELAY in context/environment
        # requires a properly configured backend to run the tests.
        super().setUpClass()
        cls.keycloak_backend = cls.env.ref("keycloak.keycloak_backend")
        partner_vals = {
            "email": "email@provider.com",
            "name": "Firstname Lastname",
        }
        cls.partner = cls.env["res.partner"].create(partner_vals)
        # normal flow would be to create the user through the wizard.
        # however we want to skip the creation on the backend
        cls.vals_user = {
            "keycloak_id": "ecf8ea6d-c490",  # would normally be given by the backend
            "keycloak_backend_id": cls.keycloak_backend.id,
            "partner_id": cls.partner.id,
            "username": "username",
            "enabled": True,
        }
