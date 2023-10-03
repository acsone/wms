# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import Command, _, fields
from odoo.tests.common import TransactionCase


class TestReconcileSamePaymentMode(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_1 = cls.env["res.partner"].create({"name": "partner1"})
        cls.partner_2 = cls.env["res.partner"].create({"name": "partner2"})

        cls.product = cls.env.ref("product.product_product_8")
        cls.journal_bank = cls.env["res.partner.bank"].create(
            {
                "acc_number": "GB95LOYD87430237296288",
                "partner_id": cls.env.user.company_id.id,
            }
        )
        cls.journal = cls.env["account.journal"].create(
            {
                "name": "BANK TEST",
                "code": "TEST",
                "type": "bank",
                "bank_account_id": cls.journal_bank.id,
            }
        )
        cls.payment_mode1 = cls.env["account.payment.mode"].create(
            {
                "name": "Payment Mode Inbound 1",
                "payment_method_id": cls.env.ref(
                    "account.account_payment_method_manual_in"
                ).id,
                "bank_account_link": "variable",
                "variable_journal_ids": [(4, cls.journal.id, _)],
            }
        )

        cls.payment_mode2 = cls.env["account.payment.mode"].create(
            {
                "name": "Payment Mode Inbound 2",
                "payment_method_id": cls.env.ref(
                    "account.account_payment_method_manual_in"
                ).id,
                "bank_account_link": "variable",
                "variable_journal_ids": [(4, cls.journal.id, _)],
            }
        )
        cls.tax = cls.env["account.tax"].create(
            {
                "name": "Unittest tax",
                "price_include": False,
                "amount_type": "percent",
                "amount": "10",
            }
        )
        cls.sepa_ct = cls.journal.outbound_payment_method_line_ids.filtered(
            lambda l: l.code == "manual"
        )
        cls.invoice1 = cls._create_invoice(
            "out_invoice", cls.payment_mode1, partner=cls.partner_1
        )
        cls.invoice2 = cls._create_invoice(
            "out_invoice", cls.payment_mode2, partner=cls.partner_1
        )
        cls.refund = cls._refund_invoice(cls.invoice2)
        cls._create_payment(cls.partner_1, 50, cls.payment_mode1, "customer")
        cls._create_payment(cls.partner_1, 50, cls.payment_mode2, "customer")

        cls.invoice_supplier = cls._create_invoice(
            "in_invoice", cls.payment_mode2, partner=cls.partner_2
        )
        cls.refund_supplier = cls._refund_invoice(cls.invoice2)
        cls._create_payment(cls.partner_2, 50, cls.payment_mode1, "supplier")
        cls._create_payment(cls.partner_2, 50, cls.payment_mode2, "supplier")

    @classmethod
    def _create_payment(cls, partner, amount, payment_mode, partner_type):
        payment = cls.env["account.payment"].create(
            {
                "journal_id": cls.journal.id,
                "payment_method_line_id": cls.sepa_ct.id,
                "payment_type": "inbound" if partner_type == "customer" else "outbound",
                "date": fields.Date.today(),
                "amount": amount,
                "partner_id": partner.id,
                "partner_type": partner_type,
            }
        )
        payment.line_ids.payment_mode_id = payment_mode
        payment.action_post()

    @classmethod
    def _create_invoice(
        cls, invoice_type, payment_mode, partner=None, product=None, tax=None
    ):
        if not partner:
            partner = cls.partner_1

        if not product:
            product = cls.product

        if not tax:
            tax = cls.tax
        values = {
            "invoice_date": fields.Date.today(),
            "date": fields.Date.today(),
            "partner_id": partner.id,
            "payment_mode_id": payment_mode.id,
            "move_type": invoice_type,
            "invoice_line_ids": [
                Command.create(
                    {
                        "name": product.name,
                        "product_id": product.id,
                        "quantity": 1,
                        "product_uom_id": cls.env.ref("uom.product_uom_unit").id,
                        "price_unit": 100.0,
                        "tax_ids": [Command.set(tax.ids)],
                    },
                )
            ],
        }
        invoice = (
            cls.env["account.move"]
            .with_context(default_move_type=invoice_type)
            .create(values)
        )

        invoice.action_post()
        return invoice

    @classmethod
    def _refund_invoice(cls, invoice, post=True):
        credit_note_wizard = (
            cls.env["account.move.reversal"]
            .with_context(
                **{
                    "active_ids": invoice.ids,
                    "active_id": invoice.id,
                    "active_model": "account.move",
                }
            )
            .create(
                {
                    "refund_method": "refund",
                    "reason": "refund",
                    "journal_id": invoice.journal_id.id,
                }
            )
        )
        invoice_refund = cls.env["account.move"].browse(
            credit_note_wizard.reverse_moves()["res_id"]
        )
        invoice_refund.ref = invoice_refund.id
        if post:
            invoice_refund.action_post()
        return invoice_refund

    def test_00_get_widget_info_for_invoice_one_and_only_invoice1(self):
        infos = self.invoice1.invoice_outstanding_credits_debits_widget
        content = infos["content"]

        move_line_ids_to_keep = (
            self.env["account.move.line"].search(
                [
                    ("move_type", "=", "out_refund"),
                    ("account_id.account_type", "=", "asset_receivable"),
                    ("partner_id", "=", self.partner_1.id),
                ]
            )
            | self.env["account.move.line"].search(
                [
                    ("move_type", "=", "entry"),
                    ("account_id.account_type", "=", "asset_receivable"),
                    ("partner_id", "=", self.partner_1.id),
                ]
            )
        ).ids

        move_line_ids_to_reject = (
            self.env["account.move.line"]
            .search(
                [
                    ("move_type", "=", "entry"),
                    ("account_id.account_type", "=", "asset_receivable"),
                    ("partner_id", "=", self.partner_1.id),
                    ("payment_mode_id", "=", self.payment_mode2.id),
                ]
            )
            .ids
        )
        # All account move lines should be attached to invoice1, not to invoice2 neither to refund
        for el in content:
            self.assertTrue(el["id"] in move_line_ids_to_keep)
        for el in content:
            self.assertTrue(el["id"] not in move_line_ids_to_reject)

    def test_01_ignore_payment_mode_if_supplier(self):
        self.invoice_supplier._compute_payments_widget_to_reconcile_info()
        infos = self.invoice_supplier.invoice_outstanding_credits_debits_widget
        content = infos["content"]

        move_line_ids_to_keep = (
            self.env["account.move.line"].search(
                [
                    ("move_type", "=", "in_refund"),
                    ("account_id.account_type", "=", "liability_payable"),
                    ("partner_id", "=", self.partner_2.id),
                ]
            )
            | self.env["account.move.line"].search(
                [
                    ("move_type", "=", "entry"),
                    ("account_id.account_type", "=", "liability_payable"),
                    ("partner_id", "=", self.partner_2.id),
                ]
            )
        ).ids

        move_line_ids_to_reject = (
            self.env["account.move.line"]
            .search(
                [
                    ("move_type", "=", "entry"),
                    ("account_id.account_type", "=", "liability_payable"),
                    ("partner_id", "=", self.partner_2.id),
                    ("payment_mode_id", "=", self.payment_mode1.id),
                ]
            )
            .ids
        )
        # All account move lines should be attached to invoice1, not to invoice2 neither to refund
        for el in content:
            self.assertTrue(el["id"] in move_line_ids_to_keep)
        for el in content:
            self.assertTrue(el["id"] not in move_line_ids_to_reject)
