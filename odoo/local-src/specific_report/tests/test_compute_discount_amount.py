# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestComputeDiscountAmount(TransactionCase):
    def setUp(self):
        super(TestComputeDiscountAmount, self).setUp()

        self.tax = self.env["account.tax"].create(
            {
                'name': 'Unittest tax',
                'price_include': False,
                'amount_type': 'percent',
                'amount': '0',
            }
        )

        self.p1 = self.env['product.product'].create(
            {'name': 'Unittest P1', 'taxes_id': [(6, False, [self.tax.id])]}
        )

        self.partner = self.env['res.partner'].create(
            {'name': 'Unittest partner', 'ref': '84023435243'}
        )

        self.account_type = self.env['account.account.type'].create(
            {'name': 'Test', 'type': 'receivable'}
        )
        self.account = self.env['account.account'].create(
            {
                'name': 'Test account',
                'code': 'TEST',
                'user_type_id': self.account_type.id,
                'reconcile': True,
            }
        )

        self.invoice = self.env['account.invoice'].create(
            {
                'partner_id': self.partner.id,
                'account_id': self.account.id,
                'invoice_line_ids': [
                    (
                        0,
                        False,
                        {
                            'name': self.p1.name,
                            'product_id': self.p1.id,
                            'quantity': 1,
                            'uom_id': self.ref('product.product_uom_unit'),
                            'price_unit': 100.0,
                            'account_id': self.account.id,
                        },
                    )
                ],
            }
        )

    def test_discount_amount(self):
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
