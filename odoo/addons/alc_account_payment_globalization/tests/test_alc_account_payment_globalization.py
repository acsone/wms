# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import Command, fields
from odoo.tests import common


class TestAlcAccountPaymentGlobalization(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_1 = cls.env["res.partner"].create({"name": "partner1"})
        cls.partner_2 = cls.env["res.partner"].create({"name": "partner2"})
        cls.partner_3 = cls.env["res.partner"].create({"name": "partner3"})

        cls.payment_mode = cls.env["account.payment.mode"].create(
            {
                "name": "Inbound payment mode",
                "company_id": cls.env.ref("base.main_company").id,
                "bank_account_link": "variable",
                "payment_method_id": cls.env.ref(
                    "account.account_payment_method_manual_in"
                ).id,
                "payment_type": "inbound",
            }
        )

        # associate the partner 3 to an bank account and create a banking mandate
        # for this account
        cls.mandate = cls.partner_3.valid_mandate_id
        if not cls.mandate:
            bank_account = cls.env.ref("account_payment_mode.res_partner_12_iban")
            bank_account.partner_id = cls.partner_3

            mandate = cls.env["account.banking.mandate"].create(
                {"partner_bank_id": bank_account.id, "signature_date": "2015-01-01"}
            )
            mandate.validate()
            cls.mandate = cls.partner_3.valid_mandate_id
        cls.partner_3.customer_payment_mode_id = cls.payment_mode
        cls.payment_term = cls.env.ref("account.account_payment_term_advance")
        cls.AccountAccount = cls.env["account.account"]
        cls.account_receivable_1 = cls.AccountAccount.create(
            {
                "name": "Receive account",
                "code": "440000demo1",
                "account_type": "asset_receivable",
                "reconcile": True,
            }
        )
        cls.account_receivable_2 = cls.AccountAccount.create(
            {
                "name": "Receive account",
                "code": "440000demo2",
                "account_type": "asset_receivable",
                "reconcile": True,
            }
        )
        cls.account_revenue = cls.AccountAccount.create(
            {
                "name": "Revenue account",
                "code": "702",
                "account_type": "income",
            }
        )
        cls.journal = cls.env["account.journal"].create(
            {
                "name": "Sales Journal - (test)",
                "code": "TSAJ",
                "type": "sale",
                "refund_sequence": True,
            }
        )
        cls.partner_1.property_account_receivable_id = cls.account_receivable_1
        cls.partner_1.property_account_payable_id = cls.account_revenue
        cls.partner_2.property_account_receivable_id = cls.account_receivable_1
        cls.partner_2.property_account_payable_id = cls.account_revenue
        cls.partner_3.property_account_receivable_id = cls.account_receivable_1
        cls.partner_3.property_account_payable_id = cls.account_revenue

        cls.invoice_model = cls.env["account.move"].with_context(
            default_move_type="out_invoice"
        )
        cls.product = cls.env.ref("product.product_product_4")
        cls.tax_fixed = cls.env["account.tax"].create(
            {
                "sequence": 10,
                "name": "Tax 10.0 (Fixed)",
                "amount": 10.0,
                "amount_type": "fixed",
                "include_base_amount": True,
            }
        )
        cls.invoice_partner_1_1_receivable_1 = cls._create_invoice(
            cls.partner_1, cls.product
        )
        cls.invoice_partner_1_2_receivable_1 = cls._create_invoice(
            cls.partner_1, cls.product
        )
        cls.invoice_partner_2_1_receivable_1 = cls._create_invoice(
            cls.partner_2, cls.product
        )
        cls.invoice_partner_2_2_receivable_1 = cls._create_invoice(
            cls.partner_2, cls.product, price_unit=200
        )
        cls.invoice_partner_2_1_receivable_2 = cls._create_invoice(
            cls.partner_2, cls.product, price_unit=200, account=cls.account_receivable_2
        )

    @classmethod
    def _create_invoice(cls, partner, product, price_unit=100, qty=5, account=None):
        account = account or cls.account_receivable_1
        partner.property_account_receivable_id = account
        invoice = cls.invoice_model.create(
            {
                "partner_id": partner.id,
                "payment_mode_id": cls.payment_mode.id,
                "invoice_line_ids": [
                    Command.create(
                        {
                            "product_id": product.id,
                            "quantity": qty,
                            "price_unit": price_unit,
                            "account_id": cls.account_revenue.id,
                            "name": "product that cost 100",
                            "tax_ids": [Command.set(cls.tax_fixed.ids)],
                        }
                    )
                ],
            }
        )
        return invoice

    def _do_globalization(self, partner, account, date=None):
        date = date or fields.Date.today()
        wizard = self.env["alc.account.payment.globalization"].create(
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
