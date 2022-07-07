# Copyright 2022 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.alc_eshop_classifieds.tests.common import TestClassifiedCase


class TestClassified(TestClassifiedCase):
    def test_send_mail(self):
        classified = self.classified_1_misc
        classified.submit()

        domain_message = [
            ("partner_ids", "in", classified.user_id.partner_id.ids),
            ("model", "=", "alc.classified"),
        ]
        message = self.env["mail.message"].search(domain_message)
        self.assertTrue(classified.name in message.subject)
