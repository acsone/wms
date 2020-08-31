# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.tests import common


class TestCsvReport(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestCsvReport, cls).setUpClass()
        cls.partner_1 = cls.env["res.partner"].create({"name": "partner1"})
        cls.partner_2 = cls.env["res.partner"].create({"name": "partner1"})
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

        cls.account_type_receivable = cls.env.ref(
            "account.data_account_type_receivable"
        )
        cls.account_type_revenue = cls.env.ref("account.data_account_type_revenue")
        cls.AccountAccount = cls.env["account.account"]
        cls.account_receivable_1 = cls.AccountAccount.create(
            {
                "name": "Receive account",
                "code": "440000_demo_1",
                "user_type_id": cls.account_type_receivable.id,
                "reconcile": True,
            }
        )
        cls.account_receivable_2 = cls.AccountAccount.create(
            {
                "name": "Receive account",
                "code": "440000_demo_2",
                "user_type_id": cls.account_type_receivable.id,
                "reconcile": True,
            }
        )
        cls.account_revenue = cls.AccountAccount.create(
            {
                "name": "Revenue account",
                "code": "702",
                "user_type_id": cls.account_type_revenue.id,
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

        cls.AccountInvoice = cls.env["account.invoice"]
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
        invoice = cls.AccountInvoice.create(
            {
                "partner_id": partner.id,
                "account_id": account.id,
                "type": "out_invoice",
                "payment_mode_id": cls.payment_mode.id,
            }
        )

        cls.env["account.invoice.line"].create(
            {
                "product_id": product.id,
                "quantity": qty,
                "price_unit": price_unit,
                "invoice_id": invoice.id,
                "account_id": cls.account_revenue.id,
                "name": "product that cost 100",
                "invoice_line_tax_ids": [(6, 0, [cls.tax_fixed.id])],
            }
        )
        invoice.compute_taxes()

        return invoice

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
        self.invoice_partner_1_1_receivable_1.action_invoice_open()
        self.invoice_partner_1_2_receivable_1.action_invoice_open()
        self.invoice_partner_2_1_receivable_1.action_invoice_open()
        self.invoice_partner_2_1_receivable_2.action_invoice_open()

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
        self.assertEqual(len(attachments), 1)
        self.assertTrue(attachments.datas_fname.endswith(".csv"))
