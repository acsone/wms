# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from freezegun import freeze_time

from odoo import Command
from odoo.tests.common import TransactionCase


class TestCurrentFiscalYearInvoices(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.account_invoice_obj = cls.env["account.move"]

        cls.payment_term = cls.env.ref("account.account_payment_term_advance")
        cls.journalrec = cls.env["account.journal"].search([("type", "=", "sale")])[0]

        cls.res_user_model = cls.env["res.users"]
        res_users_account_user = cls.env.ref("account.group_account_user")
        res_users_account_manager = cls.env.ref("account.group_account_manager")
        partner_manager = cls.env.ref("base.group_partner_manager")
        cls.account_model = cls.env["account.account"]

        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})

        cls.tax_fixed = cls.env["account.tax"].create(
            {
                "sequence": 10,
                "name": "Tax 10.0 (Fixed)",
                "amount": 10.0,
                "amount_type": "fixed",
                "type_tax_use": "sale",
            }
        )
        cls.ProductProduct = cls.env["product.product"]
        cls.product = cls.ProductProduct.create(
            {
                "name": "Product 1",
                "default_code": "987654312",
                "list_price": 20,
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "taxes_id": [Command.set(cls.tax_fixed.ids)],
            }
        )
        cls.product2 = cls.ProductProduct.create(
            {
                "name": "test product2",
                "default_code": "987654312",
                "list_price": 20,
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "taxes_id": [Command.set(cls.tax_fixed.ids)],
            }
        )

        cls.product3 = cls.ProductProduct.create(
            {
                "name": "test product3",
                "default_code": "987654313",
                "list_price": 30,
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "taxes_id": [Command.set(cls.tax_fixed.ids)],
            }
        )
        cls.product4 = cls.ProductProduct.create(
            {
                "name": "test product4",
                "default_code": "987654314",
                "list_price": 40,
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "taxes_id": [Command.set(cls.tax_fixed.ids)],
            }
        )
        cls.account_user = cls.res_user_model.create(
            {
                "name": "Accountant",
                "login": "acc",
                "email": "accountuser@yourcompany.com",
                "groups_id": [
                    Command.set([res_users_account_user.id, partner_manager.id])
                ],
            }
        )
        cls.account_manager = cls.res_user_model.create(
            {
                "name": "Adviser",
                "login": "fm",
                "email": "accountmanager@yourcompany.com",
                "groups_id": [
                    Command.set([res_users_account_manager.id, partner_manager.id])
                ],
            }
        )
        cls.account_revenue = cls.env["account.account"].create(
            {
                "name": "Revenue account",
                "code": "702",
                "account_type": "income",
            }
        )
        invoice_line_data = [
            Command.create(
                {
                    "product_id": cls.product.id,
                    "quantity": 10.0,
                    "account_id": cls.account_revenue.id,
                    "name": "product test",
                    "price_unit": 100.00,
                },
            ),
            Command.create(
                {
                    "product_id": cls.product2.id,
                    "quantity": 10.0,
                    "account_id": cls.account_revenue.id,
                    "name": "product test 2",
                    "price_unit": 100.00,
                },
            ),
        ]

        invoice_line_data2 = [
            Command.create(
                {
                    "product_id": cls.product3.id,
                    "quantity": 130.0,
                    "account_id": cls.account_revenue.id,
                    "name": "product test 3",
                    "price_unit": 500.00,
                },
            ),
            Command.create(
                {
                    "product_id": cls.product4.id,
                    "quantity": 30.0,
                    "account_id": cls.account_revenue.id,
                    "name": "product test 4",
                    "price_unit": 500.00,
                },
            ),
        ]
        cls.account_invoice_customer0 = cls.account_invoice_obj.with_user(
            cls.account_user.id
        ).create(
            {
                "name": "Test Customer Invoice",
                "move_type": "out_invoice",
                "invoice_payment_term_id": cls.payment_term.id,
                "journal_id": cls.journalrec.id,
                "partner_id": cls.partner.id,
                "invoice_line_ids": invoice_line_data,
                "date": "2020-12-02",
                "invoice_date": "2020-12-02",
            }
        )
        cls.account_invoice_customer0.action_post()
        cls.account_invoice_customer1 = cls.account_invoice_obj.with_user(
            cls.account_user.id
        ).create(
            {
                "name": "Test Customer Invoice1",
                "move_type": "out_invoice",
                "invoice_payment_term_id": cls.payment_term.id,
                "journal_id": cls.journalrec.id,
                "partner_id": cls.partner.id,
                "invoice_line_ids": invoice_line_data,
                "date": "2020-05-15",
                "invoice_date": "2020-05-15",
            }
        )
        cls.account_invoice_customer1.action_post()

        cls.account_invoice_customer2 = cls.account_invoice_obj.with_user(
            cls.account_user.id
        ).create(
            {
                "name": "Test Customer Invoice2",
                "move_type": "out_invoice",
                "invoice_payment_term_id": cls.payment_term.id,
                "journal_id": cls.journalrec.id,
                "partner_id": cls.partner.id,
                "invoice_line_ids": invoice_line_data2,
                "date": "2021-01-02",
                "invoice_date": "2021-01-02",
            }
        )
        cls.account_invoice_customer2.action_post()

    @freeze_time("2020-11-01 07:10:00")
    def test_00(self):
        """Customer invoice 1 is ignored."""
        total_invoiced_in_current_year = 100 * 10 + 100 * 10 + 500 * 30 + 500 * 130
        self.partner._compute_invoice_total_current_fiscal_year()
        self.assertEqual(
            total_invoiced_in_current_year,
            self.partner.total_invoiced_in_current_fiscal_year,
        )

    @freeze_time("2020-03-01 07:10:00")
    def test_01(self):
        """Customer invoices 0 and 2 are ignored."""
        total_invoiced_in_current_year = 100 * 10 + 100 * 10
        self.partner._compute_invoice_total_current_fiscal_year()

        self.assertEqual(
            total_invoiced_in_current_year,
            self.partner.total_invoiced_in_current_fiscal_year,
        )

    @freeze_time("2020-11-01 07:10:00")
    def test_02(self):
        """Check that we retrieve the 2 invoices using the domain from open partner history."""
        result = self.partner.action_view_partner_invoices()
        invoices = self.account_invoice_obj.search(result["domain"])
        self.assertIn(self.account_invoice_customer0.id, invoices.ids)
        self.assertIn(self.account_invoice_customer2.id, invoices.ids)
        self.assertNotIn(self.account_invoice_customer1.id, invoices.ids)
