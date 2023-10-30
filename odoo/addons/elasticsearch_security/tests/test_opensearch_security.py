# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from psycopg2.errors import UniqueViolation
from vcr_unittest import VCRTestCase

from odoo import Command
from odoo.tests.common import TransactionCase
from odoo.tools import mute_logger

from odoo.addons.queue_job.tests.common import trap_jobs


class TestOpensearchSecurity(VCRTestCase, TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.backend = cls.env.ref("connector_elasticsearch.backend_1")
        cls.backend.write(
            {
                "es_server_host": "https://localhost/",
                "opensearch_user": "user",
                "opensearch_user_password": "fake_password",
                "ssl": True,
                "role_ids": [
                    Command.create(
                        {
                            "name": "role_1",
                            "extra_backend_roles": "opendistro_security_anonymous_backendrole",
                            "body": """{"index_permissions": []}""",
                        }
                    )
                ],
            }
        )
        cls.role = cls.backend.role_ids

    def test_00(self):
        self.backend.synchronize_roles()

    def test_01(self):
        """A job is enqueued at role unlink."""
        with trap_jobs() as trap:
            self.backend.role_ids.unlink()
            trap.assert_enqueued_job(
                self.role.delete_role, args=(self.backend, "role_1")
            )
            trap.perform_enqueued_jobs()

    def test_02(self):
        """A job is enqueued at role creation."""
        with trap_jobs() as trap:
            new_role = self.backend.role_ids.create(
                {
                    "name": "role_2",
                    "body": """{"index_permissions": []}""",
                    "backend_id": self.backend.id,
                }
            )
            trap.assert_enqueued_job(new_role.put_role)

    @mute_logger("odoo.sql_db")
    def test_03(self):
        """Role name is unique by backend."""
        with self.assertRaises(UniqueViolation):
            self.backend.role_ids.create(
                {"name": "role_1", "backend_id": self.backend.id, "body": "{}"}
            )
