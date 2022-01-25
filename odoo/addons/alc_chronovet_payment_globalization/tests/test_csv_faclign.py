# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64
import csv
import StringIO

from odoo import fields
from odoo.tests import common


class TestCsvFaclign(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestCsvFaclign, cls).setUpClass()
        cls.warehouse_1 = cls.env.ref("stock.warehouse0")
        cls.warehouse_1.write(
            {
                "name": "Test Warehouse",
                "reception_steps": "one_step",
                "delivery_steps": "pick_ship",
                "code": "TST",
            }
        )
        cls.warehouse_1.pick_type_id.subcode = "PICK"

        cls.partner_1 = cls.env["res.partner"].create(
            {"name": "partner1", "ref": "1234564"}
        )
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

        cls.product = cls.env["product.product"].create(
            {
                "name": "test product1",
                "default_code": "987654321",
                "tracking": "none",
                "list_price": 20,
                "uom_id": cls.env.ref("product.product_uom_unit").id,
                "type": "product",
            }
        )
        cls.product2 = cls.env["product.product"].create(
            {
                "name": "test product2",
                "default_code": "987654312",
                "tracking": "none",
                "list_price": 20,
                "uom_id": cls.env.ref("product.product_uom_unit").id,
                "type": "product",
            }
        )

        cls.tax_fixed = cls.env["account.tax"].create(
            {
                "sequence": 10,
                "name": "Tax 10.0 (Fixed)",
                "amount": 10.0,
                "amount_type": "fixed",
                "include_base_amount": True,
            }
        )
        cls.so1 = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner_1.id,
                "warehouse_id": cls.warehouse_1.id,
                "partner_invoice_id": cls.partner_1.id,
                "partner_shipping_id": cls.partner_1.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": cls.product.name,
                            "product_id": cls.product.id,
                            "product_uom_qty": 5.0,
                            "product_uom": cls.product.uom_id.id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": cls.product2.name,
                            "product_id": cls.product2.id,
                            "product_uom_qty": 15.0,
                            "product_uom": cls.product2.uom_id.id,
                        },
                    ),
                ],
            }
        )
        cls.so1.action_confirm()

        picking = cls.so1.mapped("picking_ids").filtered(
            lambda p: p.picking_type_subcode == "PICK"
        )

        picking.action_confirm()
        picking.action_assign()
        for pack_op in picking.pack_operation_ids:
            pack_op.qty_done = pack_op.product_qty
        picking.action_done()
        shipping = cls.so1.mapped("picking_ids").filtered(
            lambda p: p.picking_type_code == "outgoing"
        )

        shipping.action_confirm()
        shipping.action_assign()
        for pack_op in shipping.pack_operation_ids:
            pack_op.qty_done = pack_op.product_qty
        shipping.action_done()

        invoice_ids = cls.so1.action_invoice_create(final=True)
        cls.invoices = cls.env["account.invoice"].browse(invoice_ids)

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
        for invoice in self.invoices:
            invoice.payment_mode_id = self.payment_mode.id
            for line in invoice.invoice_line_ids:
                line.write(
                    {
                        "account_id": self.account_revenue.id,
                        "invoice_line_tax_ids": [(6, 0, [self.tax_fixed.id])],
                    }
                )

            invoice.action_invoice_open()

        account_globalization = self._do_globalization(
            self.partner_1, self.account_receivable_1
        )
        self.assertTrue(account_globalization)

        attachments = self.env["ir.attachment"].search(
            [
                ("res_id", "=", account_globalization.id),
                ("res_model", "=", account_globalization._name),
            ]
        )
        # Faclign & Facpied are generated now
        self.assertEqual(len(attachments), 2)
        for attachment in attachments:
            self.assertTrue(attachment.datas_fname.endswith(".csv"))

    def test_01_make_sure_faclign_content_is_complete(self):
        """
        We create a refund from scratch : in that case, we wnat to make sure that
        a line for the refund is created in the faclign file.
        """
        for invoice in self.invoices:
            invoice.payment_mode_id = self.payment_mode.id
            for line in invoice.invoice_line_ids:
                line.write(
                    {
                        "account_id": self.account_revenue.id,
                        "invoice_line_tax_ids": [(6, 0, [self.tax_fixed.id])],
                    }
                )
            invoice.action_invoice_open()
        refund = self.env["account.invoice"].create(
            {
                "partner_id": self.partner_1.id,
                "account_id": self.account_receivable_1.id,
                "payment_mode_id": self.payment_mode.id,
                "invoice_line_ids": [
                    (
                        0,
                        False,
                        {
                            "name": self.product.name,
                            "product_id": self.product.id,
                            "quantity": 1,
                            "uom_id": self.env.ref("product.product_uom_unit").id,
                            "price_unit": 100.0,
                            "account_id": self.account_revenue.id,
                            "invoice_line_tax_ids": [(6, 0, [self.tax_fixed.id])],
                        },
                    )
                ],
                "type": "out_refund",
            }
        )
        refund.action_invoice_open()
        account_globalization = self._do_globalization(
            self.partner_1, self.account_receivable_1
        )
        self.assertTrue(account_globalization)

        attachments = self.env["ir.attachment"].search(
            [
                ("res_id", "=", account_globalization.id),
                ("res_model", "=", account_globalization._name),
            ]
        )
        # Faclign & Facpied are generated now
        self.assertEqual(len(attachments), 2)

        for attachment in attachments:
            self.assertTrue(attachment.datas_fname.endswith(".csv"))
            if attachment.datas_fname == u"__faclign.csv":
                data = base64.b64decode(attachment.datas)
                reader = csv.DictReader(
                    StringIO.StringIO(data),
                    delimiter=";",
                    lineterminator="\r\n",
                    quoting=csv.QUOTE_ALL,
                )
                for row in reader:
                    if row["TYPE"] == "out_refund":
                        self.assertEqual(row["CDART"], u"987654321")
                        self.assertEqual(row["DESART"], u"test product1")
                        self.assertEqual(row["CFACT"], u"1234564")
                        self.assertEqual(row["CLIVR"], u"1234564")
                        self.assertEqual(row["TOTALHT"], "-100.0")
                        self.assertEqual(row["QTFACT"], "1.0")
                        self.assertEqual(row["TVA"], "10.0")
                        self.assertEqual(row["MONTHT"], "-100.0")
                        self.assertEqual(row["MONTTVA"], "-10.0")
