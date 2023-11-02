# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestAccountInvoiceSupplierRefUnique(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass()

        # ENVIRONMENTS
        cls.account_account = cls.env["account.account"]
        cls.account_move = cls.env["account.move"].with_context(
            **{"tracking_disable": True}
        )

        # INSTANCES
        cls.partner = cls.env.ref("base.res_partner_2")
        # Account for invoice
        cls.account = cls.account_account.search(
            [
                (
                    "account_type",
                    "=",
                    "asset_receivable",
                )
            ],
            limit=1,
        )

        # Activate unique number check
        cls.env.company.check_invoice_supplier_number_mandatory = True

    def test_check_mandatory_supplier_invoice_number(self):
        # A new invoice instance with an existing supplier_invoice_number
        with self.assertRaises(ValidationError):
            self.account_move.create(
                {
                    "partner_id": self.partner.id,
                    "move_type": "in_invoice",
                }
            )
        # A new invoice instance with a supplier_invoice_number
        invoice = self.account_move.create(
            {
                "partner_id": self.partner.id,
                "move_type": "in_invoice",
                "supplier_invoice_number": "ABC123",
            }
        )
        # try to remove the supplier invoice number
        with self.assertRaises(ValidationError):
            invoice.supplier_invoice_number = False
