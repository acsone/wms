# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.tests.common import SavepointCase


class TestDeliveryNoteRecipient(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestDeliveryNoteRecipient, cls).setUpClass()

        cls.Users = cls.env["res.users"]

        # Company
        company_vals = {
            "name": "company_name_test",
            "ref": "12344566777878",
            "email": "company.mail.test@company",
        }

        cls.company_test = cls.env["res.partner"].create(company_vals)

        # Partners test 1 without email
        partner_no_mail_vals = {
            "name": "partner_1",
            "ref": "12344566777879",
            "parent_id": cls.company_test.id,
        }

        # Partners test 2 with email
        partner_with_mail_vals = {
            "name": "partner_2",
            "ref": "12344566777880",
            "email": "partner.2.mail.test@company",
            "parent_id": cls.company_test.id,
        }

        cls.partner_no_mail = cls.env["res.partner"].create(partner_no_mail_vals)
        cls.partner_with_mail = cls.env["res.partner"].create(partner_with_mail_vals)

    def test_mail_send_to_partner_no_mail(self):
        """Use company mail if recipient partner has no email."""
        values = {"partner_ids": [self.partner_no_mail.id]}
        self.assertEqual(
            self.env["stock.picking"]._delivery_note_recipient_ids(values),
            [self.company_test.id],
        )

    def test_mail_send_to_partner_with_mail(self):
        """Use partner mail if recipient partner has an email."""
        values = {"partner_ids": [self.partner_with_mail.id]}
        self.assertEqual(
            self.env["stock.picking"]._delivery_note_recipient_ids(values),
            [self.partner_with_mail.id],
        )

    def test_mail_send_to_company_test(self):
        """Use company mail if recipient is the company."""
        values = {"partner_ids": [self.partner_with_mail.id]}
        self.assertEqual(
            self.env["stock.picking"]._delivery_note_recipient_ids(values),
            [self.partner_with_mail.id],
        )

    def test_mail_send_all(self):
        """Do not duplicate recipients"""
        values = {
            "partner_ids": [
                self.partner_with_mail.id,
                self.partner_no_mail.id,
                self.company_test.id,
            ]
        }
        self.assertEqual(
            set(self.env["stock.picking"]._delivery_note_recipient_ids(values)),
            {self.partner_with_mail.id, self.company_test.id},
        )
