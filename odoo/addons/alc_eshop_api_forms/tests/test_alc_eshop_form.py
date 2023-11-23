# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import contextlib
from unittest import mock

from odoo.exceptions import ValidationError
from odoo.tests.common import SavepointCase


class MailRecorder:
    def __init__(self, env):
        self.env = env
        self.Mail = self.env["mail.mail"]
        self.created_mails = self.Mail

    @contextlib.contextmanager
    def record_created_mails(self):
        self.created_mails = self.Mail
        mails = self.Mail.search([])
        # disable mail sending to be sure that the email
        # is not auto deleted
        with mock.patch.object(mails.__class__, "send"):
            yield
        self.created_mails = self.Mail.search([]) - mails


class TestAlcEShopForm(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, queue_job__no_delay=True))
        cls.mail_recorder = MailRecorder(cls.env)
        cls.partner = cls.env["res.partner"].create(
            {"name": "partner", "email": "partner@test.com"}
        )
        cls.EShopForm = cls.env["alc.eshop.form"]
        cls.vals = {
            "name": "test form",
            "code": "TEST",
            "audience": "authenticated_only",
            "email": "laurent.mignon@acsone.eu",
            "email_subject": "test subject",
            "form": "{}",
        }
        cls.form = cls.EShopForm.create(cls.vals)

    def test_default_code(self):
        # this one was manually given
        self.assertEqual(self.form.code, "TEST")

        vals = dict(self.vals, audience="public_only", name="code form", code=False)
        form = self.EShopForm.create(vals)
        self.assertEqual(form.code, "COD_PUB")

        vals = dict(self.vals, name="code form", code=False)
        form = self.EShopForm.create(vals)
        self.assertEqual(form.code, "COD_AUT")

    def test_send_no_partner(self):
        with self.mail_recorder.record_created_mails():
            email = self.form._send_collected_info({"A": "a", "B": "b"})
        self.assertTrue(email)
        self.assertEqual(1, len(self.mail_recorder.created_mails))

    def test_send_from_parnter(self):
        messages = self.partner.message_ids
        with self.mail_recorder.record_created_mails():
            email = self.form._send_collected_info({"A": "a", "B": "b"}, self.partner)
        self.assertTrue(email)
        self.assertEqual(1, len(self.mail_recorder.created_mails))
        new_message = self.partner.message_ids - messages
        self.assertEqual(1, len(new_message))

    def test_form_validation(self):
        with self.assertRaises(ValidationError), self.env.cr.savepoint():
            self.form.form_options = "[123"
        self.form.form_options = "{}"
        with self.assertRaises(ValidationError), self.env.cr.savepoint():
            self.form.form = "[123"
        self.form.form = "{}"
