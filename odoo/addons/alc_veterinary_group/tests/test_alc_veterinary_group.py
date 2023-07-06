# -*- coding: utf-8 -*-
# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests.common import SavepointCase


class TestAlcVeterinaryGroup(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestAlcVeterinaryGroup, cls).setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.veterinary_group_model = cls.env["veterinary.group"]
        cls.partner_model = cls.env["res.partner"]

        cls.tomorrow = datetime.now() + timedelta(days=1)
        cls.yesterday = datetime.now() - timedelta(days=1)

        cls.alcyonnaire_group = cls.veterinary_group_model.create(
            {"name": "Alcyonnaire", "is_alcyonnaire": True}
        )
        cls.partner = cls.partner_model.create({"name": "Partner"})

        cls.partner_veterinary = cls.partner_model.create(
            {
                "name": "Partner Veterinary",
                "veterinary_group_ids": [(4, cls.alcyonnaire_group.id)],
            }
        )

        cls.partner_veterinary_with_contract = cls.partner_model.create(
            {
                "name": "Partner Veterinary",
                "veterinary_group_ids": [(4, cls.alcyonnaire_group.id)],
                "date_start_contract_alcyonnaire": cls.yesterday,
            }
        )

    def test_set_alcyonnaire_and_date_start_same_time(self):
        self.partner.write(
            {
                "veterinary_group_ids": [(4, self.alcyonnaire_group.id)],
                "date_start_contract_alcyonnaire": fields.Date.today(),
            }
        )
        self.assertTrue(self.partner.is_alcyonnaire)
        self.assertTrue(self.partner.is_alcyonnaire_under_contract)

    def test_set_date_start_not_allowed_on_non_veterinary(self):
        with self.assertRaises(ValidationError), self.cr.savepoint():
            self.partner.date_start_contract_alcyonnaire = fields.Date.today()
        self.partner_veterinary.date_start_contract_alcyonnaire = fields.Date.today()

    def test_set_date_end_not_allowed_on_non_veterinary(self):
        with self.assertRaises(ValidationError), self.cr.savepoint():
            self.partner.date_end_contract_alcyonnaire = fields.Date.today()

    def test_set_date_end_not_allowed_without_date_start(self):
        with self.assertRaises(ValidationError), self.cr.savepoint():
            self.partner_veterinary.date_end_contract_alcyonnaire = fields.Date.today()
        self.partner_veterinary.write(
            {
                "date_start_contract_alcyonnaire": fields.Date.today(),
                "date_end_contract_alcyonnaire": fields.Date.today(),
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
                "date_end_contract_alcyonnaire": fields.Date.today(),
                "veterinary_group_ids": [(3, self.alcyonnaire_group.id)],
            }
        )

    def test_remove_alcyonnaire_with_contract_no_end_date_not_allowed_2(self):
        with self.assertRaises(ValidationError), self.cr.savepoint():
            self.alcyonnaire_group.write(
                {"partner_ids": [(3, self.partner_veterinary_with_contract.id)]}
            )
        self.partner_veterinary_with_contract.write(
            {"date_end_contract_alcyonnaire": fields.Date.today()}
        )
        self.alcyonnaire_group.write(
            {"partner_ids": [(3, self.partner_veterinary_with_contract.id)]}
        )
