# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase, post_install, at_install

import logging

_logger = logging.getLogger(__name__)


class TestPricelistDiscount(TransactionCase):

    def setUp(self):
        super(TestPricelistDiscount, self).setUp()

        self.tax = self.env["account.tax"].create({
            'name': 'Unittest tax',
            'price_include': False,
            'amount_type': 'percent',
            'amount': '0',
        })

        self.product_category = self.env['product.category'].create({
            'name': 'Unittest category'
        })

        self.supplier = self.env['res.partner'].create({
            'name': 'Unittest supplier',
            'ref': '749248',
        })

        self.supplierinfo1 = self.env['product.supplierinfo'].create({
            'name': self.supplier.id,
            'discount_sale': 10,
        })

        self.p1 = self.env['product.product'].create({
            'name': 'Unittest P1',
            'taxes_id': [(6, False, [self.tax.id])],
            'seller_ids': [(6, 0, [self.supplierinfo1.id])],
        })

        self.supplierinfo2 = self.env['product.supplierinfo'].create({
            'name': self.supplier.id,
            'discount_sale': 10,
        })

        self.p2 = self.env['product.product'].create({
            'name': 'Unittest P2',
            'categ_id': self.product_category.id,
            'taxes_id': [(6, False, [self.tax.id])],
            'seller_ids': [(6, 0, [self.supplierinfo2.id])],
        })

        self.main_pricelist = self.env['product.pricelist'].create({
            'name': 'Unittest Pricelist',
            'item_ids': [
                (0, False, {
                    'applied_on': '0_product_variant',
                    'product_id': self.p1.id,
                    'compute_price': 'fixed',
                    'fixed_price': 100,
                }),
                (0, False, {
                    'applied_on': '0_product_variant',
                    'product_id': self.p2.id,
                    'compute_price': 'fixed',
                    'fixed_price': 200,
                })
            ],
        })

        self.discount_pricelist_id = self.env['product.pricelist'].create({
            'name': 'Unittest Discount Pricelist',
            'item_ids': [
                (0, False, {
                    'applied_on': '2_product_category',
                    'categ_id': self.product_category.id,
                    'compute_price': 'percentage',
                    'percent_price': 5,
                })
            ],
        })

        self.partner = self.env['res.partner'].create({
            'name': 'Unittest partner',
            'ref': '8893294',
            'property_product_pricelist': self.main_pricelist.id,
            'supplier_promotion_sale_allowed': True,
            'discount_pricelist_id': self.discount_pricelist_id.id,
        })

        self.sale = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'order_line': [
                (0, False, {
                    'name': self.p1.name,
                    'product_id': self.p1.id,
                    'product_uom_qty': 1,
                    'product_uom': self.ref('product.product_uom_unit'),
                }),
                (0, False, {
                    'name': self.p2.name,
                    'product_id': self.p2.id,
                    'product_uom_qty': 2,
                    'product_uom': self.ref('product.product_uom_unit'),
                }),
            ]
        })
        self.sale.onchange_partner_id_discount_pricelist()
        self.sol_p1 = self.sale.order_line[0]
        self.sol_p2 = self.sale.order_line[1]

    @post_install(True)
    @at_install(False)
    def test_onchange_partner(self):
        partner = self.env['res.partner'].create({
            'name': 'Unittest other partner',
            'ref': '99584783994',
        })
        sale = self.env['sale.order'].create({
            'partner_id': partner.id
        })

        self.assertFalse(sale.supplier_promotion_allowed)
        self.assertFalse(sale.discount_pricelist_id)

        sale.partner_id = self.partner
        sale.onchange_partner_id_discount_pricelist()

        self.assertTrue(sale.supplier_promotion_allowed)
        self.assertEqual(
            self.discount_pricelist_id, sale.discount_pricelist_id
        )

    @post_install(True)
    @at_install(False)
    def test_sale_discounts(self):
        for line in self.sale.order_line:
            line.product_id_change()
            line.onchange_product_id_reset_discount()

        self.assertEqual(100, self.sol_p1.price_unit)
        self.assertEqual(10, self.sol_p1.discount2)
        self.assertEqual(0, self.sol_p1.discount3)

        self.assertEqual(90, self.sol_p1.price_subtotal)

        self.assertEqual(200, self.sol_p2.price_unit)
        self.assertEqual(10, self.sol_p2.discount2)
        self.assertEqual(5, self.sol_p2.discount3)

        # There is 2 p2 in sale order so subtotal = 171 * 2
        self.assertEqual(342, self.sol_p2.price_subtotal)

        self.assertEqual(432, self.sale.amount_total)

    @post_install(True)
    @at_install(False)
    def test_sale_discounts_tax_excluded(self):
        self.tax.amount = 20

        for line in self.sale.order_line:
            line.product_id_change()
            line.onchange_product_id_reset_discount()

        self.assertEqual(100, self.sol_p1.price_unit)
        self.assertEqual(10, self.sol_p1.discount2)
        self.assertEqual(0, self.sol_p1.discount3)

        self.assertEqual(90, self.sol_p1.price_subtotal)
        self.assertEqual(18, self.sol_p1.price_tax)
        self.assertAlmostEqual(108, self.sol_p1.price_total)

        self.assertEqual(200, self.sol_p2.price_unit)
        self.assertEqual(10, self.sol_p2.discount2)
        self.assertEqual(5, self.sol_p2.discount3)

        # There is 2 p2 in sale order so subtotal = 171 * 2
        self.assertEqual(342, self.sol_p2.price_subtotal)
        self.assertEqual(68.4, self.sol_p2.price_tax)
        self.assertAlmostEqual(410.4, self.sol_p2.price_total)

        self.assertEqual(518.4, self.sale.amount_total)

    @post_install(True)
    @at_install(False)
    def test_sale_discounts_tax_included(self):
        self.tax.amount = 20
        self.tax.price_include = True

        for line in self.sale.order_line:
            line.product_id_change()
            line.onchange_product_id_reset_discount()

        self.assertEqual(100, self.sol_p1.price_unit)
        self.assertEqual(10, self.sol_p1.discount2)
        self.assertEqual(0, self.sol_p1.discount3)

        self.assertEqual(75, self.sol_p1.price_subtotal)
        self.assertEqual(15, self.sol_p1.price_tax)
        self.assertAlmostEqual(90, self.sol_p1.price_total)

        self.assertEqual(200, self.sol_p2.price_unit)
        self.assertEqual(10, self.sol_p2.discount2)
        self.assertEqual(5, self.sol_p2.discount3)

        # There is 2 p2 in sale order so subtotal = 171 * 2
        self.assertEqual(285, self.sol_p2.price_subtotal)
        self.assertEqual(57, self.sol_p2.price_tax)
        self.assertAlmostEqual(342, self.sol_p2.price_total)

        self.assertEqual(432, self.sale.amount_total)

    @post_install(True)
    @at_install(False)
    def test_no_supplier_promotion(self):
        self.sale.supplier_promotion_allowed = False

        for line in self.sale.order_line:
            line.product_id_change()
            line.onchange_product_id_reset_discount()

        self.assertEqual(100, self.sol_p1.price_unit)
        self.assertEqual(0, self.sol_p1.discount2)
        self.assertEqual(0, self.sol_p1.discount3)

        self.assertEqual(100, self.sol_p1.price_subtotal)

        self.assertEqual(200, self.sol_p2.price_unit)
        self.assertEqual(0, self.sol_p2.discount2)
        self.assertEqual(5, self.sol_p2.discount3)

        # There is 2 p2 in sale order so subtotal = 190 * 2
        self.assertEqual(380, self.sol_p2.price_subtotal)

        self.assertEqual(480, self.sale.amount_total)

    def test_manually_change_unit_price(self):
        self.sol_p2.product_id_change()
        self.sol_p2.onchange_product_id_reset_discount()

        self.assertEqual(200, self.sol_p2.price_unit)
        self.assertEqual(10, self.sol_p2.discount2)
        self.assertEqual(5, self.sol_p2.discount3)

        # There is 2 p2 in sale order so subtotal = 171 * 2
        self.assertEqual(342, self.sol_p2.price_subtotal)

        # Change unit price
        self.sol_p2.price_unit = 150

        self.assertEqual(150, self.sol_p2.price_unit)
        self.assertEqual(10, self.sol_p2.discount2)
        self.assertEqual(5, self.sol_p2.discount3)

        # There is 2 p2 in sale order so subtotal = 171 * 2
        self.assertEqual(256.5, self.sol_p2.price_subtotal)

    def test_manually_change_discount(self):
        self.sol_p2.product_id_change()
        self.sol_p2.onchange_product_id_reset_discount()

        self.assertEqual(200, self.sol_p2.price_unit)
        self.assertEqual(10, self.sol_p2.discount2)
        self.assertEqual(5, self.sol_p2.discount3)

        # There is 2 p2 in sale order so subtotal = 171 * 2
        self.assertEqual(342, self.sol_p2.price_subtotal)

        # Change supplier promotion
        self.sol_p2.discount2 = 8.24
        self.sol_p2._compute_amount()

        self.assertEqual(200, self.sol_p2.price_unit)
        self.assertEqual(8.24, self.sol_p2.discount2)
        self.assertEqual(5, self.sol_p2.discount3)

        # There is 2 p2 in sale order so subtotal = 174.34 * 2
        self.assertEqual(348.68, self.sol_p2.price_subtotal)

        # Change alcyon discount
        self.sol_p2.discount3 = 3.83
        self.sol_p2._compute_amount()

        self.assertEqual(200, self.sol_p2.price_unit)
        self.assertEqual(8.24, self.sol_p2.discount2)
        self.assertEqual(3.83, self.sol_p2.discount3)

        # There is 2 p2 in sale order so subtotal = 174.34 * 2
        self.assertEqual(352.98, self.sol_p2.price_subtotal)

        # Change both
        self.sol_p2.discount2 = 20
        self.sol_p2.discount3 = 10
        self.sol_p2._compute_amount()

        self.assertEqual(200, self.sol_p2.price_unit)
        self.assertEqual(20, self.sol_p2.discount2)
        self.assertEqual(10, self.sol_p2.discount3)

        # There is 2 p2 in sale order so subtotal = 174.34 * 2
        self.assertEqual(288, self.sol_p2.price_subtotal)

        # Change quantity
        self.sol_p2.product_uom_qty = 1

        self.assertEqual(200, self.sol_p2.price_unit)
        self.assertEqual(20, self.sol_p2.discount2)
        self.assertEqual(10, self.sol_p2.discount3)

        self.assertEqual(144, self.sol_p2.price_subtotal)

        # Bug when only alcyon was filled
        # (And discount3 should not be recompute)
        self.sol_p2.price_unit = 0.46
        self.sol_p2.discount2 = 0
        self.sol_p2.discount3 = 5
        self.sol_p2._compute_amount()

        self.assertEqual(0.46, self.sol_p2.price_unit)
        self.assertEqual(0, self.sol_p2.discount2)
        self.assertEqual(5, self.sol_p2.discount3)

        self.assertEqual(0.44, self.sol_p2.price_subtotal)

    @post_install(True)
    @at_install(False)
    def test_create_invoice(self):
        self.tax.amount = 20

        for line in self.sale.order_line:
            line.product_id_change()
            line.onchange_product_id_reset_discount()

        self.sale.action_confirm()

        invoices = self.sale.action_invoice_create(final=True)
        self.assertEqual(1, len(invoices))
        invoice = self.env['account.invoice'].browse(invoices[0])

        self.assertEqual(518.4, self.sale.amount_total)
        self.assertEqual(86.4, self.sale.amount_tax)

        # Check invoice

        # Check lines
        line1 = invoice.invoice_line_ids.filtered(
            lambda l: l.product_id == self.p1
        )
        self.assertEqual(100, line1.price_unit)
        self.assertEqual(10, line1.discount2)
        self.assertEqual(0, line1.discount3)
        if line1.price_subtotal != 90:
            _logger.info(
                """=======Mythic bug is back this is a debug info======="""
            )
            _logger.info(
                """price_unit: {}
                price_subtotal: {}
                discount: {}
                discount2: {},
                discount3: {}""".format(
                    line1.price_unit,
                    line1.price_subtotal,
                    line1.discount,
                    line1.discount2,
                    line1.discount3,
                ))
            _logger.info("""=======End of debug info=======""")
        self.assertEqual(90, line1.price_subtotal)

        line2 = invoice.invoice_line_ids.filtered(
            lambda l: l.product_id == self.p2
        )
        self.assertEqual(200, line2.price_unit)
        self.assertEqual(10, line2.discount2)
        self.assertEqual(5, line2.discount3)
        self.assertEqual(342, line2.price_subtotal)

        # Check taxes
        self.assertEqual(1, len(invoice.tax_line_ids))
        self.assertEqual(86.4, invoice.tax_line_ids[0].amount)

        # Check totals
        self.assertEqual(518.4, invoice.amount_total)
        self.assertEqual(86.4, invoice.amount_tax)

    def test_coverage(self):
        """ Test special cases for coverage.
        """

        # Supplier promotion 100%
        self.supplierinfo1.discount_sale = 100
        self.supplierinfo2.discount_sale = 100
        self.tax.amount = 20

        for line in self.sale.order_line:
            line.product_id_change()
            line.onchange_product_id_reset_discount()

        self.assertEqual(100, self.sol_p1.price_unit)
        self.assertEqual(100, self.sol_p1.discount2)
        self.assertEqual(0, self.sol_p1.discount3)

        self.assertEqual(0, self.sol_p1.price_subtotal)
        self.assertEqual(0, self.sol_p1.price_tax)
        self.assertAlmostEqual(0, self.sol_p1.price_total)

        self.assertEqual(200, self.sol_p2.price_unit)
        self.assertEqual(100, self.sol_p2.discount2)
        self.assertEqual(5, self.sol_p2.discount3)

        self.assertEqual(0, self.sol_p2.price_subtotal)
        self.assertEqual(0, self.sol_p2.price_tax)
        self.assertAlmostEqual(0, self.sol_p2.price_total)

        self.assertEqual(0, self.sale.amount_total)

    def test_commercial_fields(self):
        sub_partner = self.env['res.partner'].create({
            'parent_id': self.partner.id,
            'ref': '234788894934',
            'name': 'Unittest sub partner',
            'supplier_promotion_sale_allowed': True,
        })

        self.sale.write({
            'supplier_promotion_allowed': False,
            'discount_pricelist_id': False,
            'partner_id': sub_partner.id,
        })

        self.sale.onchange_partner_id_discount_pricelist()
        self.assertTrue(self.sale.supplier_promotion_allowed)
        self.assertEqual(
            self.discount_pricelist_id, self.sale.discount_pricelist_id
        )
