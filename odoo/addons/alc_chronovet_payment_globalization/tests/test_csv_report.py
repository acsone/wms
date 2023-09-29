# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.alc_account_payment_globalization.tests.common import (
    TestAlcAccountPaymentGlobalizationCommon,
)


class TestCsvReport(TestAlcAccountPaymentGlobalizationCommon):
    def _do_globalization(self, partner, account, date=None):
        date = date or fields.Date.today()
        wizard = self.env["alc.chronovet.payment.globalization"].create(
            {
                "partner_id": partner.id,
                "account_id": account.id,
                "date": date,
                "journal_id": self.journal.id,
                "payment_mode_id": self.payment_mode.id,
            }
        )
        res = wizard.doit()
        return self.env["account.move"].browse(res["res_id"])

    def test_00(self):
        """
        Data:

            2 open invoices for partner 1 and receivable_1 account
            1 open invoice for partner 2 and receivable_1 account
            1 draft invoice for partner 2 and receivable_1 account
            1 open invoice for partner 2 and receivable_2 account
        Test Case:
            globalize For receivable account on partner 3
            make the after_globalization and check we get the invoices back before print csv
        Expected result;
        """
        self.invoice_partner_1_1_receivable_1.action_post()
        self.invoice_partner_1_2_receivable_1.action_post()
        self.invoice_partner_2_1_receivable_1.action_post()
        self.invoice_partner_2_1_receivable_2.action_post()

        account_globalization = self._do_globalization(
            self.partner_3, self.account_receivable_1
        )
        self.assertTrue(account_globalization)

        attachments = self.env["ir.attachment"].search(
            [
                ("res_id", "=", account_globalization.id),
                ("res_model", "=", account_globalization._name),
            ]
        )
        # Faclign & Facpied are generated here
        self.assertEqual(len(attachments), 2)
        for attachment in attachments:
            self.assertTrue(attachment.name.endswith(".csv"))
