# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.exceptions import AccessError
from odoo.tests.common import TransactionCase


class TestDecimalPrecisionPermissions(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.DecimalPrecision = cls.env["decimal.precision"]

        cls.group_user = cls.env.ref("base.group_user")
        cls.group_base_manager = cls.env.ref("alc_base_security.base_manager")

        cls.base_user = cls.env["res.users"].create(
            {
                "name": "Base user (Read-Only)",
                "login": "base_user",
                "email": "base_user@example.com",
                "groups_id": [Command.set([cls.group_user.id])],
            }
        )

        cls.manager_user = cls.env["res.users"].create(
            {
                "name": "Manager user",
                "login": "manager_user",
                "email": "manager_user@example.com",
                "groups_id": [
                    Command.set([cls.group_user.id, cls.group_base_manager.id])
                ],
            }
        )

        cls.admin_user = cls.env.ref("base.user_admin")

        cls.test_precision = cls.env["decimal.precision"].create(
            {
                "name": "Test Precision Unit",
                "digits": 5,
            }
        )

    def test_01_base_user_read_access(self):
        precisions = self.DecimalPrecision.with_user(self.base_user).search([])
        self.assertIn(
            self.test_precision,
            precisions,
            "Base user should be able to read the specific test precision.",
        )

    def test_02_base_user_write_access_denied(self):
        with self.assertRaises(
            AccessError,
            msg="Base user should not be able to write to decimal.precision.",
        ):
            self.test_precision.with_user(self.base_user).write({"digits": 6})

    def test_03_base_user_create_access_denied(self):
        with self.assertRaises(
            AccessError, msg="Base user should not be able to create decimal.precision."
        ):
            self.DecimalPrecision.with_user(self.base_user).create(
                {"name": "New Test Precision", "digits": 2}
            )

    def test_04_base_user_unlink_access_denied(self):
        with self.assertRaises(
            AccessError, msg="Base user should not be able to unlink decimal.precision."
        ):
            self.test_precision.with_user(self.base_user).unlink()

        self.assertTrue(
            self.test_precision.exists(),
            "Precision should still exist after failed unlink.",
        )

    def test_05_manager_full_access(self):
        new_precision = self.DecimalPrecision.with_user(self.manager_user).create(
            {"name": "Manager Created Precision", "digits": 7}
        )
        self.assertTrue(
            new_precision.exists(),
            "Manager user should be able to create decimal.precision.",
        )
        self.assertEqual(
            new_precision.digits, 7, "Created precision should have correct digits."
        )

        precisions = self.DecimalPrecision.with_user(self.manager_user).search(
            [("name", "=", "Manager Created Precision")]
        )
        self.assertTrue(
            precisions, "Manager user should be able to read created precision."
        )

        new_precision.with_user(self.manager_user).write({"digits": 8})
        self.assertEqual(
            new_precision.digits,
            8,
            "Manager user should be able to write to decimal.precision.",
        )

        new_precision.with_user(self.manager_user).unlink()
        self.assertFalse(
            new_precision.exists(),
            "Manager user should be able to unlink decimal.precision.",
        )

    def test_06_admin_full_access(self):
        admin_precision = self.DecimalPrecision.with_user(self.admin_user).create(
            {"name": "Admin Created Precision", "digits": 10}
        )
        self.assertTrue(
            admin_precision.exists(),
            "Admin should be able to create decimal.precision.",
        )

        admin_precision.with_user(self.admin_user).write({"digits": 11})
        self.assertEqual(
            admin_precision.digits,
            11,
            "Admin should be able to write to decimal.precision.",
        )

        admin_precision.with_user(self.admin_user).unlink()
        self.assertFalse(
            admin_precision.exists(),
            "Admin should be able to unlink decimal.precision.",
        )
