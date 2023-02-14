# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import os

from odoo.tests.common import TransactionCase


class TestExternalFax(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        os.environ["OVH_FAX_EMAIL_DOMAIN"] = "domain.test"
        os.environ["OVH_FAX_NUMBER"] = "077123456"
        os.environ["OVH_FAX_PASSWORD"] = "secret_pwd"
        cls.fax = cls.env.ref("alc_external_fax.ovh")
        cls.attachment = cls.env["ir.attachment"].create(
            {
                "type": "binary",
                "res_model": "sale.order",
                "name": "fax.pdf",
                "mimetype": "text/plain",
                "raw": b"fake pdf content",
            }
        )

    def test_email_from_default(self):
        new_mail = self.fax.send("012 0234 23", self.attachment.id)
        user = self.env.user
        user_email = f'"{user.name}" <{user.email}>'
        self.assertEqual(new_mail.email_from, user_email)

    def test_email_from_env(self):
        os.environ["OVH_FAX_EMAIL_FROM"] = "from@domain.test"
        new_mail = self.fax.send("012 0234 23", self.attachment.id)
        self.assertEqual(new_mail.email_from, "from@domain.test")

    def test_email_recipient(self):
        """Check generation of email recipient."""
        recipient = self.fax.email_recipient('079"123 45 67')
        self.assertEqual(recipient, "0791234567@domain.test")

    def test_body(self):
        """Check generation of the body."""
        body = self.fax.body()
        self.assertEqual(body, "password:secret_pwd")

    def test_email_send(self):
        new_mail = self.fax.send("012 0234 23", self.attachment.id)
        self.assertEqual(new_mail[0].state, "sent")
