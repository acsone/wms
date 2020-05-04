# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestComputeDiscountAmount(TransactionCase):
    post_install = True
    at_install = False

    def setUp(self):
        super(TestComputeDiscountAmount, self).setUp()

        company = self.env.user.company_id
        company.tax_calculation_rounding_method = "round_globally"
        self.tax1 = self.env["account.tax"].create(
            {
                "name": "Unittest tax",
                "price_include": False,
                "amount_type": "percent",
                "amount": "0",
            }
        )

        self.p1 = self.env["product.product"].create(
            {"name": "Unittest P1", "taxes_id": [(6, False, [self.tax1.id])]}
        )

        self.partner = self.env["res.partner"].create(
            {"name": "Unittest partner", "ref": "84023435243"}
        )

        self.account_type = self.env["account.account.type"].create(
            {"name": "Test", "type": "receivable"}
        )
        self.account = self.env["account.account"].create(
            {
                "name": "Test account",
                "code": "TEST",
                "user_type_id": self.account_type.id,
                "reconcile": True,
            }
        )

    def test_discount_amount(self):
        self.invoice = self.env["account.invoice"].create(
            {
                "partner_id": self.partner.id,
                "account_id": self.account.id,
                "invoice_line_ids": [
                    (
                        0,
                        False,
                        {
                            "name": self.p1.name,
                            "product_id": self.p1.id,
                            "quantity": 1,
                            "uom_id": self.ref("product.product_uom_unit"),
                            "price_unit": 100.0,
                            "account_id": self.account.id,
                        },
                    )
                ],
            }
        )

        self.assertEqual(self.invoice.invoice_line_ids.quantity, 1)
        self.assertEqual(self.invoice.invoice_line_ids.price_unit, 100)
        self.assertEqual(self.invoice.invoice_line_ids.discount2, 0)
        self.assertEqual(self.invoice.amount_supplier_discount, 0)
        self.assertEqual(self.invoice.invoice_line_ids.discount3, 0)
        self.assertEqual(self.invoice.amount_alcyon_discount, 0)
        self.assertEqual(self.invoice.amount_discount_total, 0)
        self.assertEqual(self.invoice.invoice_line_ids.price_subtotal, 100)

        self.invoice.invoice_line_ids.discount2 = 50

        self.assertEqual(self.invoice.invoice_line_ids.quantity, 1)
        self.assertEqual(self.invoice.invoice_line_ids.price_unit, 100)
        self.assertEqual(self.invoice.invoice_line_ids.discount2, 50)
        self.assertEqual(self.invoice.amount_supplier_discount, 50)
        self.assertEqual(self.invoice.invoice_line_ids.discount3, 0)
        self.assertEqual(self.invoice.amount_alcyon_discount, 0)
        self.assertEqual(self.invoice.amount_discount_total, 50)
        self.assertEqual(self.invoice.invoice_line_ids.price_subtotal, 50)

        self.invoice.invoice_line_ids.discount3 = 50

        self.assertEqual(self.invoice.invoice_line_ids.quantity, 1)
        self.assertEqual(self.invoice.invoice_line_ids.price_unit, 100)
        self.assertEqual(self.invoice.invoice_line_ids.discount2, 50)
        self.assertEqual(self.invoice.amount_supplier_discount, 50)
        self.assertEqual(self.invoice.invoice_line_ids.discount3, 50)
        self.assertEqual(self.invoice.amount_alcyon_discount, 25)
        self.assertEqual(self.invoice.amount_discount_total, 75)
        self.assertEqual(self.invoice.invoice_line_ids.price_subtotal, 25)

        self.invoice.invoice_line_ids.quantity = 10

        self.assertEqual(self.invoice.invoice_line_ids.quantity, 10)
        self.assertEqual(self.invoice.invoice_line_ids.price_unit, 100.0)
        self.assertEqual(self.invoice.invoice_line_ids.discount2, 50)
        self.assertEqual(self.invoice.amount_supplier_discount, 50 * 10)
        self.assertEqual(self.invoice.invoice_line_ids.discount3, 50)
        self.assertEqual(self.invoice.amount_alcyon_discount, 25 * 10)
        self.assertEqual(self.invoice.amount_discount_total, 75 * 10)
        self.assertEqual(self.invoice.invoice_line_ids.price_subtotal, 25 * 10)

    def test_discount_amount_rounding(self):
        """Test that base amount to compute tax is equal to the
        sum of rounded untaxed amount on lines

        This test is based on real values. And tests base amount.
        """
        tax_group_apb = self.env.ref("specific_account.tax_group_apb")
        tax_group_antibiotics = self.env.ref("account.tax_group_taxes")
        tax_group_vat = self.env.ref("specific_data.vat_tax_group")
        tax_6 = self.env["account.tax"].create(
            {
                "name": "TEST 6% tax",
                "amount_type": "percent",
                "amount": 6.00,
                "tax_group_id": tax_group_vat.id,
                "price_include": False,
                "include_base_amount": False,
            }
        )
        tax_21 = self.env["account.tax"].create(
            {
                "name": "TEST 21% tax",
                "amount_type": "percent",
                "amount": 21.00,
                "tax_group_id": tax_group_vat.id,
                "price_include": False,
                "include_base_amount": False,
            }
        )
        tax_apb = self.env["account.tax"].create(
            {
                "name": "TEST APB",
                "amount_type": "fixed",
                "amount": 0.02292,
                "tax_group_id": tax_group_apb.id,
                "price_include": False,
                "include_base_amount": False,
            }
        )
        tax_antibio = self.env["account.tax"].create(
            {
                "name": "TEST antibio",
                "amount_type": "fixed",
                "amount": 0.01,
                "tax_group_id": tax_group_antibiotics.id,
                "price_include": False,
                "include_base_amount": False,
            }
        )
        invoice_lines = [
            # price, qty, discount2, discount3, taxes
            (6.84, 1, 0, 0, tax_21),
            (10.87, 1, 0, 5, tax_apb | tax_6),
            (12.7, 1, 0, 5, tax_21),
            (4.14, 6, 0, 0, tax_6),
            (9.66, 1, 0, 0, tax_21),
            (6.38, 1, 0, 0, tax_6),
            (87.59, 1, 0, 5, tax_antibio | tax_apb | tax_6),
            (98.08, 1, 0, 5, tax_apb | tax_6),
            (86.65, 1, 25, 5, tax_antibio | tax_apb | tax_6),
            (45.12, 1, 0, 5, tax_21),
            (31.47, 1, 0, 5, tax_apb | tax_6),
        ]

        lines_vals = []

        for price, qty, disc2, disc3, taxes in invoice_lines:
            lines_vals.append(
                (
                    0,
                    False,
                    {
                        "name": self.p1.name,
                        "product_id": self.p1.id,
                        "quantity": qty,
                        "uom_id": self.ref("product.product_uom_unit"),
                        "price_unit": price,
                        "account_id": self.account.id,
                        "discount2": disc2,
                        "discount3": disc3,
                        "invoice_line_tax_ids": [(6, 0, taxes.ids)],
                    },
                )
            )

        self.invoice = self.env["account.invoice"].create(
            {
                "partner_id": self.partner.id,
                "account_id": self.account.id,
                "invoice_line_ids": lines_vals,
            }
        )

        self.assertAlmostEqual(self.invoice.amount_without_discount, 420.20)
        self.assertAlmostEqual(self.invoice.amount_supplier_discount, 21.66)
        self.assertAlmostEqual(self.invoice.amount_alcyon_discount, 17.53)
        self.assertAlmostEqual(self.invoice.amount_untaxed_with_contribution, 381.01)
        self.assertAlmostEqual(self.invoice.amount_apb, 0.11)
        self.assertAlmostEqual(self.invoice.amount_antibiotics, 0.02)
        self.assertAlmostEqual(self.invoice.amount_only_tax, 33.57)

        # Summary
        self.assertAlmostEqual(self.invoice.amount_discount_total, 39.19)
        tax_lines = self.invoice.invoice_only_tax_ids.sorted("base")
        self.assertAlmostEqual(tax_lines[0].base, 71.43)
        self.assertAlmostEqual(tax_lines[0].amount, 15.00)
        self.assertAlmostEqual(tax_lines[1].base, 309.58)
        self.assertAlmostEqual(tax_lines[1].amount, 18.57)
        self.assertAlmostEqual(
            sum(tax_lines.mapped("base")), self.invoice.amount_untaxed_with_contribution
        )

    def test_discount_base_rounding_before_tax(self):
        """Test that base amount was rounded before tax are computed

        This test is based on fake values but offer a better coverage.
        """
        tax_group_vat = self.env.ref("specific_data.vat_tax_group")
        tax_6 = self.env["account.tax"].create(
            {
                "name": "TEST 6% tax",
                "amount_type": "percent",
                "amount": 6.00,
                "tax_group_id": tax_group_vat.id,
                "price_include": False,
                "include_base_amount": False,
            }
        )
        tax_21 = self.env["account.tax"].create(
            {
                "name": "TEST 21% tax",
                "amount_type": "percent",
                "amount": 21.00,
                "tax_group_id": tax_group_vat.id,
                "price_include": False,
                "include_base_amount": False,
            }
        )
        # force prices to get sum of taxes to uncomfortable tax sums

        # price, qty, discount2, discount3, taxes
        invoice_lines = [(1.0, 1, 25, 5, tax_21)] * 6 + [(2.0, 1, 25, 5, tax_6)] * 8

        lines_vals = []

        for price, qty, disc2, disc3, taxes in invoice_lines:
            lines_vals.append(
                (
                    0,
                    False,
                    {
                        "name": self.p1.name,
                        "product_id": self.p1.id,
                        "quantity": qty,
                        "uom_id": self.ref("product.product_uom_unit"),
                        "price_unit": price,
                        "account_id": self.account.id,
                        "discount2": disc2,
                        "discount3": disc3,
                        "invoice_line_tax_ids": [(6, 0, taxes.ids)],
                    },
                )
            )

        self.invoice = self.env["account.invoice"].create(
            {
                "partner_id": self.partner.id,
                "account_id": self.account.id,
                "invoice_line_ids": lines_vals,
            }
        )

        # Summary
        tax_lines = self.invoice.invoice_only_tax_ids.sorted("base")
        self.assertAlmostEqual(tax_lines[0].base, 0.71 * 6)
        self.assertAlmostEqual(tax_lines[1].base, 1.43 * 8)

        # test base was rounded before computing taxes
        # for taxes 21 if base is not rounded result will more: 0.9
        self.assertAlmostEqual(tax_lines[0].amount, 0.89)
        # for taxes 6 if base is not rounded result will be less: 0.68
        self.assertAlmostEqual(tax_lines[1].amount, 0.69)

        self.assertAlmostEqual(
            sum(tax_lines.mapped("base")),
            self.invoice.amount_untaxed_with_contribution,
            msg="sum(%s) != %.2f"
            % (
                ", ".join("%.2f" % t for t in tax_lines.mapped("base")),
                self.invoice.amount_untaxed_with_contribution,
            ),
        )
        self.assertAlmostEqual(
            sum(tax_lines.mapped("amount")), self.invoice.amount_only_tax
        )

        self.assertAlmostEqual(self.invoice.amount_only_tax, 1.58)
