# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from freezegun import freeze_time
from odoo.tests.common import SavepointCase


class TestCurrentFiscalYearInvoices(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestCurrentFiscalYearInvoices, cls).setUpClass()

        # cls.partner = cls.env.ref('base.res_partner_3')
        cls.account_invoice_obj = cls.env["account.invoice"]

        cls.payment_term = cls.env.ref("account.account_payment_term_advance")
        cls.journalrec = cls.env["account.journal"].search([("type", "=", "sale")])[0]

        cls.res_user_model = cls.env["res.users"]

        cls.main_company = cls.env.ref("base.main_company")
        account_user_type = cls.env.ref("account.data_account_type_receivable")
        res_users_account_user = cls.env.ref("account.group_account_user")
        res_users_account_manager = cls.env.ref("account.group_account_manager")
        partner_manager = cls.env.ref("base.group_partner_manager")
        cls.account_model = cls.env["account.account"]

        cls.partner = cls.env["res.partner"].create(
            {"name": "Test Partner", "customer": True}
        )

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
                "tracking": "none",
                "list_price": 20,
                "uom_id": cls.env.ref("product.product_uom_unit").id,
                "taxes_id": [(6, False, [cls.tax_fixed.id])],
            }
        )
        cls.product2 = cls.ProductProduct.create(
            {
                "name": "test product2",
                "default_code": "987654312",
                "tracking": "none",
                "list_price": 20,
                "uom_id": cls.env.ref("product.product_uom_unit").id,
                "taxes_id": [(6, False, [cls.tax_fixed.id])],
            }
        )

        cls.product3 = cls.ProductProduct.create(
            {
                "name": "test product3",
                "default_code": "987654313",
                "tracking": "none",
                "list_price": 30,
                "uom_id": cls.env.ref("product.product_uom_unit").id,
                "taxes_id": [(6, False, [cls.tax_fixed.id])],
            }
        )
        cls.product4 = cls.ProductProduct.create(
            {
                "name": "test product4",
                "default_code": "987654314",
                "tracking": "none",
                "list_price": 40,
                "uom_id": cls.env.ref("product.product_uom_unit").id,
                "taxes_id": [(6, False, [cls.tax_fixed.id])],
            }
        )
        cls.account_user = cls.res_user_model.with_context(
            {"no_reset_password": True}
        ).create(
            dict(
                name="Accountant",
                company_id=cls.main_company.id,
                login="acc",
                email="accountuser@yourcompany.com",
                groups_id=[(6, 0, [res_users_account_user.id, partner_manager.id])],
            )
        )
        cls.account_manager = cls.res_user_model.with_context(
            {"no_reset_password": True}
        ).create(
            dict(
                name="Adviser",
                company_id=cls.main_company.id,
                login="fm",
                email="accountmanager@yourcompany.com",
                groups_id=[(6, 0, [res_users_account_manager.id, partner_manager.id])],
            )
        )

        cls.account_rec1_id = cls.account_model.sudo(cls.account_manager.id).create(
            dict(
                code="cust_acc",
                name="customer account",
                user_type_id=account_user_type.id,
                reconcile=True,
            )
        )

        invoice_line_data = [
            (
                0,
                0,
                {
                    "product_id": cls.product.id,
                    "quantity": 10.0,
                    "account_id": cls.env["account.account"]
                    .search(
                        [
                            (
                                "user_type_id",
                                "=",
                                cls.env.ref("account.data_account_type_revenue").id,
                            )
                        ],
                        limit=1,
                    )
                    .id,
                    "name": "product test",
                    "price_unit": 100.00,
                },
            ),
            (
                0,
                0,
                {
                    "product_id": cls.product2.id,
                    "quantity": 10.0,
                    "account_id": cls.env["account.account"]
                    .search(
                        [
                            (
                                "user_type_id",
                                "=",
                                cls.env.ref("account.data_account_type_revenue").id,
                            )
                        ],
                        limit=1,
                    )
                    .id,
                    "name": "product test 2",
                    "price_unit": 100.00,
                },
            ),
        ]

        invoice_line_data2 = [
            (
                0,
                0,
                {
                    "product_id": cls.product3.id,
                    "quantity": 130.0,
                    "account_id": cls.env["account.account"]
                    .search(
                        [
                            (
                                "user_type_id",
                                "=",
                                cls.env.ref("account.data_account_type_revenue").id,
                            )
                        ],
                        limit=1,
                    )
                    .id,
                    "name": "product test 3",
                    "price_unit": 500.00,
                },
            ),
            (
                0,
                0,
                {
                    "product_id": cls.product4.id,
                    "quantity": 30.0,
                    "account_id": cls.env["account.account"]
                    .search(
                        [
                            (
                                "user_type_id",
                                "=",
                                cls.env.ref("account.data_account_type_revenue").id,
                            )
                        ],
                        limit=1,
                    )
                    .id,
                    "name": "product test 4",
                    "price_unit": 500.00,
                },
            ),
        ]
        cls.account_invoice_customer0 = cls.account_invoice_obj.sudo(
            cls.account_user.id
        ).create(
            dict(
                name="Test Customer Invoice",
                reference_type="none",
                payment_term_id=cls.payment_term.id,
                journal_id=cls.journalrec.id,
                partner_id=cls.partner.id,
                account_id=cls.account_rec1_id.id,
                invoice_line_ids=invoice_line_data,
                date="2020-12-02",
                date_invoice="2020-12-02",
                state="paid",
            )
        )

        cls.account_invoice_customer1 = cls.account_invoice_obj.sudo(
            cls.account_user.id
        ).create(
            dict(
                name="Test Customer Invoice1",
                reference_type="none",
                payment_term_id=cls.payment_term.id,
                journal_id=cls.journalrec.id,
                partner_id=cls.partner.id,
                account_id=cls.account_rec1_id.id,
                invoice_line_ids=invoice_line_data,
                date="2020-05-15",
                date_invoice="2020-05-15",
                state="paid",
            )
        )

        cls.account_invoice_customer2 = cls.account_invoice_obj.sudo(
            cls.account_user.id
        ).create(
            dict(
                name="Test Customer Invoice2",
                reference_type="none",
                payment_term_id=cls.payment_term.id,
                journal_id=cls.journalrec.id,
                partner_id=cls.partner.id,
                account_id=cls.account_rec1_id.id,
                invoice_line_ids=invoice_line_data2,
                date="2021-01-02",
                date_invoice="2021-01-02",
                state="open",
            )
        )

    @freeze_time("2020-11-01 07:10:00")
    def test_00(self):
        " customer invoice 1 is ignored"
        total_invoiced_in_current_year = 100 * 10 + 100 * 10 + 500 * 30 + 500 * 130
        self.partner._invoice_total_current_fiscal_year()

        self.assertEqual(
            total_invoiced_in_current_year,
            self.partner.total_invoiced_in_current_fiscal_year,
        )

    @freeze_time("2020-03-01 07:10:00")
    def test_01(self):
        " customer invoices 0 and 2 are ignored"
        total_invoiced_in_current_year = 100 * 10 + 100 * 10
        self.partner._invoice_total_current_fiscal_year()

        self.assertEqual(
            total_invoiced_in_current_year,
            self.partner.total_invoiced_in_current_fiscal_year,
        )

    @freeze_time("2020-11-01 07:10:00")
    def test_02(self):
        """ Check that we retrieve the 2 invoices using the domain from open partner history """
        result = self.partner.open_partner_history()
        invoices = self.account_invoice_obj.search(result["domain"])
        self.assertIn(self.account_invoice_customer0.id, invoices.ids)
        self.assertIn(self.account_invoice_customer2.id, invoices.ids)
        self.assertNotIn(self.account_invoice_customer1.id, invoices.ids)
