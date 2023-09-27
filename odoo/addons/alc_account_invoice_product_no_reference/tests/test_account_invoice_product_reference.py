# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import Form, TransactionCase


class TestAccountInvoiceProductReference(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Partner",
            }
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "default_code": "12345",
            }
        )

    def test_invoice(self):
        # Create an invoice and check if the added product line has
        # no default code in description
        with Form(
            self.env["account.move"].with_context(default_move_type="out_invoice")
        ) as invoice_form:
            invoice_form.partner_id = self.partner
            with invoice_form.invoice_line_ids.new() as line_form:
                line_form.product_id = self.product
        invoice = invoice_form.save()

        self.assertEqual("Test Product", invoice.invoice_line_ids[0].name)
        # Check if the display name is not the name alone
        self.assertNotEqual("Test Product", self.product.display_name)
