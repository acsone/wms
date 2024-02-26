# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import TestAlcAccountPaymentGlobalizationCommon


class TestAlcAccountPaymentGlobalization(TestAlcAccountPaymentGlobalizationCommon):
    def test_00(self):
        """
        Data:

            2 open invoices for partner 1 and receivable_1 account
            1 open invoice for partner 2 and receivable_1 account
            1 draft invoice for partner 2 and receivable_1 account
            1 open invoice for partner 2 and receivable_2 account
        Test Case:
            globalize For receivable account on partner 3
        Expected result;
            A new account move with 4 lines:
            * 2 lines for partner 1 (credit)
            * 1 line for partner 2 (credit)
            * 1 line for partner 3  (debit)
            Open invoices are now paid
        """
        self.invoice_partner_1_1_receivable_1.action_post()
        self.invoice_partner_1_2_receivable_1.action_post()
        self.invoice_partner_2_1_receivable_1.action_post()
        self.invoice_partner_2_1_receivable_2.action_post()
        self.assertEqual(self.invoice_partner_1_1_receivable_1.state, "posted")
        self.assertEqual(self.invoice_partner_1_2_receivable_1.state, "posted")
        self.assertEqual(self.invoice_partner_2_1_receivable_1.state, "posted")
        self.assertEqual(self.invoice_partner_2_2_receivable_1.state, "draft")
        self.assertEqual(self.invoice_partner_2_1_receivable_2.state, "posted")
        account_globalization = self._do_globalization(
            self.partner_3, self.account_receivable_1
        )
        self.assertTrue(account_globalization)
        self.assertEqual(len(account_globalization.line_ids), 4)
        partner_1_lines = account_globalization.line_ids.filtered(
            lambda l: l.partner_id == self.partner_1
        )
        self.assertEqual(len(partner_1_lines), 2)
        self.assertEqual(partner_1_lines.mapped("reconciled"), [True, True])
        partner_2_line = account_globalization.line_ids.filtered(
            lambda l: l.partner_id == self.partner_2
        )
        self.assertEqual(len(partner_2_line), 1)
        self.assertEqual(partner_2_line.reconciled, True)
        partner_3_line = account_globalization.line_ids.filtered(
            lambda l: l.partner_id == self.partner_3
        )
        self.assertEqual(len(partner_3_line), 1)

        # partner_3_line is the globalization line
        # we must have the mandate and the payment mode on globalization line
        self.assertEqual(partner_3_line.payment_mode_id, self.payment_mode)
        self.assertEqual(partner_3_line.move_id.mandate_id, self.mandate)

        self.assertEqual(self.invoice_partner_1_1_receivable_1.payment_state, "paid")
        self.assertEqual(self.invoice_partner_1_2_receivable_1.payment_state, "paid")
        self.assertEqual(self.invoice_partner_2_1_receivable_1.payment_state, "paid")
        self.assertEqual(
            self.invoice_partner_2_1_receivable_2.payment_state, "not_paid"
        )
