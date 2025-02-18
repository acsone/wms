# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta

from odoo import Command, fields
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestAlcVeterinaryGroup(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.veterinary_group_model = cls.env["veterinary.group"]
        cls.partner_model = cls.env["res.partner"]
        cls.today = fields.Date.today()
        cls.tomorrow = datetime.now() + timedelta(days=1)
        cls.yesterday = datetime.now() - timedelta(days=1)

        cls.alcyonnaire_group = cls.veterinary_group_model.create(
            {"name": "Alcyonnaire", "is_alcyonnaire": True}
        )
        cls.partners = cls.partner_model.create(
            [
                {"name": "Partner"},
                {
                    "name": "Partner Veterinary no contract",
                    "veterinary_group_ids": [Command.link(cls.alcyonnaire_group.id)],
                },
                {
                    "name": "Partner Veterinary under contract",
                    "veterinary_group_ids": [Command.link(cls.alcyonnaire_group.id)],
                    "date_start_contract_alcyonnaire": cls.yesterday,
                },
            ]
        )
        cls.partner_veterinary_with_contract = cls.partners.filtered(
            "date_start_contract_alcyonnaire"
        )
        cls.partner_veterinary = (
            cls.partners.filtered("veterinary_group_ids")
            - cls.partner_veterinary_with_contract
        )
        cls.partner = cls.partners - cls.partners.filtered("veterinary_group_ids")

    def test_set_alcyonnaire_and_date_start_same_time(self):
        self.partner.write(
            {
                "veterinary_group_ids": [Command.link(self.alcyonnaire_group.id)],
                "date_start_contract_alcyonnaire": self.today,
            }
        )
        self.assertTrue(self.partner.is_alcyonnaire)
        self.assertTrue(self.partner.is_alcyonnaire_under_contract)

    def test_set_date_start_not_allowed_on_non_veterinary(self):
        with self.assertRaises(ValidationError), self.cr.savepoint():
            self.partner.date_start_contract_alcyonnaire = self.today
        self.partner_veterinary.date_start_contract_alcyonnaire = self.today

    def test_set_date_end_not_allowed_on_non_veterinary(self):
        with self.assertRaises(ValidationError), self.cr.savepoint():
            self.partner.date_end_contract_alcyonnaire = self.today

    def test_set_date_end_not_allowed_without_date_start(self):
        with self.assertRaises(ValidationError), self.cr.savepoint():
            self.partner_veterinary.date_end_contract_alcyonnaire = self.today
        self.partner_veterinary.write(
            {
                "date_start_contract_alcyonnaire": self.today,
                "date_end_contract_alcyonnaire": self.today,
            }
        )

    def test_set_date_start_tomorrow_not_allowed(self):
        with self.assertRaises(ValidationError), self.cr.savepoint():
            self.partner_veterinary.date_start_contract_alcyonnaire = self.tomorrow

    def test_set_date_end_tomorrow_not_allowed(self):
        with self.assertRaises(ValidationError), self.cr.savepoint():
            self.partner_veterinary_with_contract.date_end_contract_alcyonnaire = (
                self.tomorrow
            )

    def test_is_alcyonnaire_under_contract(self):
        self.assertTrue(
            self.partner_veterinary_with_contract.is_alcyonnaire_under_contract
        )
        self.assertFalse(self.partner_veterinary.is_alcyonnaire_under_contract)
        self.assertFalse(self.partner.is_alcyonnaire_under_contract)
        self.partner_veterinary.write(
            {"date_start_contract_alcyonnaire": self.yesterday}
        )
        self.assertTrue(self.partner_veterinary.is_alcyonnaire_under_contract)
        self.partner_veterinary.write(
            {
                "date_start_contract_alcyonnaire": self.yesterday,
                "date_end_contract_alcyonnaire": self.yesterday,
            }
        )
        self.assertFalse(self.partner_veterinary.is_alcyonnaire_under_contract)

    def test_remove_alcyonnaire_with_contract_no_end_date_not_allowed(self):
        with self.assertRaises(ValidationError), self.cr.savepoint():
            self.partner_veterinary_with_contract.write(
                {"veterinary_group_ids": [(3, self.alcyonnaire_group.id)]}
            )
        self.partner_veterinary_with_contract.write(
            {
                "date_end_contract_alcyonnaire": self.today,
                "veterinary_group_ids": [(3, self.alcyonnaire_group.id)],
            }
        )

    def test_remove_alcyonnaire_with_contract_no_end_date_not_allowed_2(self):
        with self.assertRaises(ValidationError), self.cr.savepoint():
            self.alcyonnaire_group.write(
                {"partner_ids": [(3, self.partner_veterinary_with_contract.id)]}
            )
        self.partner_veterinary_with_contract.write(
            {"date_end_contract_alcyonnaire": self.today}
        )
        self.alcyonnaire_group.write(
            {"partner_ids": [(3, self.partner_veterinary_with_contract.id)]}
        )

    def test_vet_efficiency(self):
        self.assertTrue(
            self.partner_veterinary_with_contract.is_alcyonnaire_under_contract
        )
        self.assertFalse(
            self.partner_veterinary_with_contract.is_exclusive_vet_efficiency_member
        )
        partners = self.env["res.partner"].search(
            [("is_valid_vet_efficiency_member", "=", True)]
        )
        self.assertEqual(len(partners), 0)
        partners = self.env["res.partner"].search(
            [("is_valid_vet_efficiency_member", "=", False)]
        )
        self.assertIn(self.partner_veterinary_with_contract, partners)
        self.partner_veterinary_with_contract.is_exclusive_vet_efficiency_member = True
        partners = self.env["res.partner"].search(
            [("is_valid_vet_efficiency_member", "=", True)]
        )
        self.assertEqual(self.partner_veterinary_with_contract, partners)
        self.partner_veterinary.is_exclusive_vet_efficiency_member = True
        # only partners under contract are valid
        partners = self.env["res.partner"].search(
            [("is_valid_vet_efficiency_member", "=", True)]
        )
        self.assertEqual(self.partner_veterinary_with_contract, partners)
        for domain in [
            [("is_valid_vet_efficiency_member", "!=", False)],
            [("is_valid_vet_efficiency_member", "=", True)],
            [("is_valid_vet_efficiency_member", "in", [True])],
            [("is_valid_vet_efficiency_member", "not in", [False])],
        ]:
            partners = self.env["res.partner"].search(domain)
            self.assertEqual(self.partner_veterinary_with_contract, partners)
