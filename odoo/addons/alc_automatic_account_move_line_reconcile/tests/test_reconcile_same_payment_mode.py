# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json

from odoo import _
from odoo.tests.common import SavepointCase


class TestReconcileSamePaymentMode(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestReconcileSamePaymentMode, cls).setUpClass()
        cls.partner_1 = cls.env["res.partner"].create({"name": "partner1"})

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
        cls.account_type = cls.env["account.account.type"].create(
            {"name": "Test", "type": "receivable"}
        )
        cls.tax = cls.env["account.tax"].create(
            {
                "name": "Unittest tax",
                "price_include": False,
                "amount_type": "percent",
                "amount": "10",
            }
        )
        cls.account = cls.env["account.account"].create(
            {
                "name": "Test account",
                "code": "TEST",
                "user_type_id": cls.account_type.id,
                "reconcile": True,
            }
        )
        cls.invoice1 = cls._create_invoice(
            "out_invoice", cls.account, cls.payment_mode1
        )
        cls.invoice2 = cls._create_invoice(
            "out_invoice", cls.account, cls.payment_mode2
        )
        invoice1_account_move_lines = cls.env["account.move.line"].search(
            [("invoice_id", "=", cls.invoice1.id)]
        )
        for line in invoice1_account_move_lines:
            line.payment_mode_id = cls.payment_mode1.id
        invoice2_account_move_lines = cls.env["account.move.line"].search(
            [("invoice_id", "=", cls.invoice2.id)]
        )
        for line in invoice2_account_move_lines:
            line.payment_mode_id = cls.payment_mode2.id
        cls.refund_wiz = (
            cls.env["account.invoice.refund"]
            .with_context(active_ids=cls.invoice2.ids)
            .create({"filter_refund": "refund", "description": "test"})
        )
        refund_id = cls.refund_wiz.invoice_refund().get("domain")[1][2]
        cls.refund = cls.env["account.invoice"].browse(refund_id)
        cls.refund.state = "open"
        refund_account_move_lines = cls.env["account.move.line"].search(
            [("invoice_id", "=", cls.refund.id)]
        )
        for line in refund_account_move_lines:
            line.payment_mode_id = cls.payment_mode2.id

    @classmethod
    def _create_invoice(
        cls, invoice_type, account, payment_mode, partner=None, product=None, tax=None
    ):
        if not partner:
            partner = cls.partner_1

        if not product:
            product = cls.product

        if not tax:
            tax = cls.tax

        invoice = cls.env["account.invoice"].create(
            {
                "partner_id": partner.id,
                "account_id": account.id,
                "payment_mode_id": payment_mode.id,
                "invoice_line_ids": [
                    (
                        0,
                        False,
                        {
                            "name": product.name,
                            "product_id": product.id,
                            "quantity": 1,
                            "uom_id": cls.env.ref("product.product_uom_unit").id,
                            "price_unit": 100.0,
                            "account_id": account.id,
                            "invoice_line_tax_ids": [(6, 0, [tax.id])],
                        },
                    )
                ],
                "type": invoice_type,
                "reconciled": False,
            }
        )

        invoice.action_invoice_open()
        return invoice

    def test_00_get_widget_info_for_invoice_one_and_only_invoice1(self):
        self.invoice1.state = "open"
        json_infos = self.invoice1.outstanding_credits_debits_widget
        infos = json.loads(json_infos)
        content = infos["content"]

        move_line_ids_to_keep = (
            self.env["account.move.line"]
            .search(
                [
                    ("account_id", "=", self.account.id),
                    ("partner_id", "=", self.partner_1.id),
                    ("payment_mode_id", "=", self.payment_mode1.id),
                ]
            )
            .ids
        )

        move_line_ids_to_reject = (
            self.env["account.move.line"]
            .search(
                [
                    ("account_id", "=", self.account.id),
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
