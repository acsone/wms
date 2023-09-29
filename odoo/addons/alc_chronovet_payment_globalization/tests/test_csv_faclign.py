# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import csv
from io import StringIO

from odoo import Command, fields

from odoo.addons.alc_account_payment_globalization.tests.common import (
    TestAlcAccountPaymentGlobalizationCommon,
)


class TestCsvFaclign(TestAlcAccountPaymentGlobalizationCommon):
    @classmethod
    def _do_transfer(cls, picking):
        picking.action_confirm()
        picking.action_assign()
        for move in picking.move_ids:
            move.quantity_done = move.product_qty
        picking._action_done()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.warehouse_1 = cls.env.ref("stock.warehouse0")
        cls.warehouse_1.write(
            {
                "name": "Test Warehouse",
                "reception_steps": "one_step",
                "delivery_steps": "pick_ship",
                "code": "TST",
            }
        )
        cls.product2 = cls.env["product.product"].create(
            {
                "name": "test product2",
                "default_code": "987654312",
                "tracking": "none",
                "list_price": 20,
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "type": "product",
            }
        )
        cls.so1 = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner_1.id,
                "warehouse_id": cls.warehouse_1.id,
                "partner_invoice_id": cls.partner_1.id,
                "partner_shipping_id": cls.partner_1.id,
                "order_line": [
                    Command.create(
                        {
                            "name": cls.product.name,
                            "product_id": cls.product.id,
                            "product_uom_qty": 5.0,
                            "product_uom": cls.product.uom_id.id,
                        },
                    ),
                    Command.create(
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

        picking = cls.so1.picking_ids.filtered(
            lambda p: p.picking_type_id.code == "internal"
        )
        cls._do_transfer(picking)
        shipping = cls.so1.mapped("picking_ids").filtered(
            lambda p: p.picking_type_code == "outgoing"
        )
        cls._do_transfer(shipping)
        cls.invoices = cls.so1._create_invoices(final=True)
        cls.product.name = "test product1"
        cls.product.default_code = "987654321"
        cls.partner_1.ref = "1234564"

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
                        "tax_ids": [Command.set(self.tax_fixed.ids)],
                    }
                )

            invoice.action_post()

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
            self.assertTrue(attachment.name.endswith(".csv"))

    def test_01_make_sure_faclign_content_is_complete(self):
        """
        We create a refund from scratch : in that case, we wnat to make sure that.

        a line for the refund is created in the faclign file.
        """
        for invoice in self.invoices:
            invoice.payment_mode_id = self.payment_mode.id
            for line in invoice.invoice_line_ids:
                line.write(
                    {
                        "account_id": self.account_revenue.id,
                        "tax_ids": [Command.set(self.tax_fixed.ids)],
                    }
                )
            invoice.action_post()
        refund = self.env["account.move"].create(
            {
                "partner_id": self.partner_1.id,
                "payment_mode_id": self.payment_mode.id,
                "invoice_line_ids": [
                    Command.create(
                        {
                            "name": self.product.name,
                            "product_id": self.product.id,
                            "quantity": 1,
                            "product_uom_id": self.env.ref("uom.product_uom_unit").id,
                            "price_unit": 100.0,
                            "account_id": self.account_revenue.id,
                            "tax_ids": [Command.set(self.tax_fixed.ids)],
                        },
                    )
                ],
                "move_type": "out_refund",
            }
        )
        refund.action_post()
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
            self.assertTrue(attachment.name.endswith(".csv"))
            if attachment.name.endswith("_faclign.csv"):
                str_io = StringIO(attachment.raw.decode())
                dict_report = list(
                    csv.DictReader(str_io, delimiter=";", quoting=csv.QUOTE_ALL)
                )
                for row in dict_report:
                    if row["TYPE"] == "out_refund":
                        self.assertEqual(row["CDART"], "987654321")
                        self.assertEqual(row["DESART"], "test product1")
                        self.assertEqual(row["CFACT"], "1234564")
                        self.assertEqual(row["CLIVR"], "1234564")
                        self.assertEqual(row["TOTALHT"], "-100.0")
                        self.assertEqual(row["QTFACT"], "1.0")
                        self.assertEqual(row["TVA"], "10.0")
                        self.assertEqual(row["MONTHT"], "-100.0")
                        self.assertEqual(row["MONTTVA"], "-10.0")
