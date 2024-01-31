# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestAccountInvoiceSupplierRefUnique(TransactionCase):
    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass()
        cls.account_move = cls.env["account.move"]
        cls.partner = cls.env.ref("base.res_partner_2")
        # Activate unique number check
        cls.env.company.check_invoice_supplier_number_mandatory = True

    def test_check_mandatory_supplier_invoice_number(self):
        # A new invoice instance without a supplier_invoice_number
        invoice = self.account_move.create(
            {
                "partner_id": self.partner.id,
                "move_type": "in_invoice",
                "invoice_date": "2023-01-01",
                "invoice_line_ids": [Command.create({"partner_id": self.partner.id})],
            }
        )
        # try to post without supplier invoice number
        with self.assertRaises(ValidationError):
            invoice.action_post()
        invoice.supplier_invoice_number = "ABC"
        invoice.action_post()
        with self.assertRaises(ValidationError):
            invoice.supplier_invoice_number = False
