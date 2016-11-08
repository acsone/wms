# -*- coding: utf-8 -*-
# © 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase


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

        self.p1 = self.env['product.product'].create({
            'name': 'Unittest P1',
            'taxes_id': [(6, False, [self.tax.id])],
        })

        self.p1 = self.env['product.product'].create({
            'name': 'Unittest P1',
            'taxes_id': [(6, False, [self.tax.id])],
        })

        self.p2 = self.env['product.product'].create({
            'name': 'Unittest P2',
            'categ_id': self.product_category.id,
            'taxes_id': [(6, False, [self.tax.id])],
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

        self.promotion_pricelist_id = self.env['product.pricelist'].create({
            'name': 'Unittest Promotion Pricelist',
            'item_ids': [
                (0, False, {
                    'applied_on': '3_global',
                    'compute_price': 'percentage',
                    'percent_price': 10,
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
            'property_product_pricelist': self.main_pricelist.id,
            'promotion_pricelist_id': self.promotion_pricelist_id.id,
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
        self.sol_p1 = self.sale.order_line[0]
        self.sol_p2 = self.sale.order_line[1]

    def test_onchange_partner(self):
        partner = self.env['res.partner'].create({
            'name': 'Unittest other partner',
        })
        sale = self.env['sale.order'].create({
            'partner_id': partner.id
        })

        self.assertFalse(sale.promotion_pricelist_id)
        self.assertFalse(sale.discount_pricelist_id)

        sale.partner_id = self.partner
        sale.onchange_partner_id_discount_pricelist()

        self.assertEqual(
            self.promotion_pricelist_id, sale.promotion_pricelist_id
        )
        self.assertEqual(
            self.discount_pricelist_id, sale.discount_pricelist_id
        )

    def test_sale_discounts(self):
        for line in self.sale.order_line:
            line.product_id_change()

        self.assertEqual(100, self.sol_p1.price_unit)
        self.assertEqual(90, self.sol_p1.price_unit_supplier)
        self.assertEqual(90, self.sol_p1.price_unit_alcyon)
        self.assertEqual(10, self.sol_p1.supplier_promotion)
        self.assertEqual(0, self.sol_p1.alcyon_discount)

        self.assertEqual(90, self.sol_p1.price_subtotal)

        self.assertEqual(200, self.sol_p2.price_unit)
        self.assertEqual(180, self.sol_p2.price_unit_supplier)
        self.assertEqual(171, self.sol_p2.price_unit_alcyon)
        self.assertEqual(10, self.sol_p2.supplier_promotion)
        self.assertEqual(5, self.sol_p2.alcyon_discount)

        # There is 2 p2 in sale order so subtotal = 171 * 2
        self.assertEqual(342, self.sol_p2.price_subtotal)

        self.assertEqual(432, self.sale.amount_total)

    def test_sale_discounts_tax_excluded(self):
        self.tax.amount = 20

        for line in self.sale.order_line:
            line.product_id_change()

        self.assertEqual(100, self.sol_p1.price_unit)
        self.assertEqual(90, self.sol_p1.price_unit_supplier)
        self.assertEqual(90, self.sol_p1.price_unit_alcyon)
        self.assertEqual(10, self.sol_p1.supplier_promotion)
        self.assertEqual(0, self.sol_p1.alcyon_discount)

        self.assertEqual(90, self.sol_p1.price_subtotal)
        self.assertEqual(18, self.sol_p1.price_tax)
        self.assertAlmostEqual(108, self.sol_p1.price_total)

        self.assertEqual(200, self.sol_p2.price_unit)
        self.assertEqual(180, self.sol_p2.price_unit_supplier)
        self.assertEqual(171, self.sol_p2.price_unit_alcyon)
        self.assertEqual(10, self.sol_p2.supplier_promotion)
        self.assertEqual(5, self.sol_p2.alcyon_discount)

        # There is 2 p2 in sale order so subtotal = 171 * 2
        self.assertEqual(342, self.sol_p2.price_subtotal)
        self.assertEqual(68.4, self.sol_p2.price_tax)
        self.assertAlmostEqual(410.4, self.sol_p2.price_total)

        self.assertEqual(518.4, self.sale.amount_total)

    def test_sale_discounts_tax_included(self):
        self.tax.amount = 20
        self.tax.price_include = True

        for line in self.sale.order_line:
            line.product_id_change()

        self.assertEqual(100, self.sol_p1.price_unit)
        self.assertEqual(90, self.sol_p1.price_unit_supplier)
        self.assertEqual(90, self.sol_p1.price_unit_alcyon)
        self.assertEqual(10, self.sol_p1.supplier_promotion)
        self.assertEqual(0, self.sol_p1.alcyon_discount)

        self.assertEqual(75, self.sol_p1.price_subtotal)
        self.assertEqual(15, self.sol_p1.price_tax)
        self.assertAlmostEqual(90, self.sol_p1.price_total)

        self.assertEqual(200, self.sol_p2.price_unit)
        self.assertEqual(180, self.sol_p2.price_unit_supplier)
        self.assertEqual(171, self.sol_p2.price_unit_alcyon)
        self.assertEqual(10, self.sol_p2.supplier_promotion)
        self.assertEqual(5, self.sol_p2.alcyon_discount)

        # There is 2 p2 in sale order so subtotal = 171 * 2
        self.assertEqual(285, self.sol_p2.price_subtotal)
        self.assertEqual(57, self.sol_p2.price_tax)
        self.assertAlmostEqual(342, self.sol_p2.price_total)

        self.assertEqual(432, self.sale.amount_total)

    def test_no_supplier_promotion(self):
        self.sale.promotion_pricelist_id = False

        for line in self.sale.order_line:
            line.product_id_change()

        self.assertEqual(100, self.sol_p1.price_unit)
        self.assertEqual(100, self.sol_p1.price_unit_supplier)
        self.assertEqual(100, self.sol_p1.price_unit_alcyon)
        self.assertEqual(0, self.sol_p1.supplier_promotion)
        self.assertEqual(0, self.sol_p1.alcyon_discount)

        self.assertEqual(100, self.sol_p1.price_subtotal)

        self.assertEqual(200, self.sol_p2.price_unit)
        self.assertEqual(200, self.sol_p2.price_unit_supplier)
        self.assertEqual(190, self.sol_p2.price_unit_alcyon)
        self.assertEqual(0, self.sol_p2.supplier_promotion)
        self.assertEqual(5, self.sol_p2.alcyon_discount)

        # There is 2 p2 in sale order so subtotal = 190 * 2
        self.assertEqual(380, self.sol_p2.price_subtotal)

        self.assertEqual(480, self.sale.amount_total)

    def test_manually_change_unit_price(self):
        self.sol_p2.product_id_change()

        self.assertEqual(200, self.sol_p2.price_unit)
        self.assertEqual(180, self.sol_p2.price_unit_supplier)
        self.assertEqual(171, self.sol_p2.price_unit_alcyon)
        self.assertEqual(10, self.sol_p2.supplier_promotion)
        self.assertEqual(5, self.sol_p2.alcyon_discount)

        # There is 2 p2 in sale order so subtotal = 171 * 2
        self.assertEqual(342, self.sol_p2.price_subtotal)

        # Change unit price
        self.sol_p2.price_unit = 150

        self.assertEqual(150, self.sol_p2.price_unit)
        self.assertEqual(135, self.sol_p2.price_unit_supplier)
        self.assertEqual(128.25, self.sol_p2.price_unit_alcyon)
        self.assertEqual(10, self.sol_p2.supplier_promotion)
        self.assertEqual(5, self.sol_p2.alcyon_discount)

        # There is 2 p2 in sale order so subtotal = 171 * 2
        self.assertEqual(256.5, self.sol_p2.price_subtotal)

    def test_manually_change_discount(self):
        self.sol_p2.product_id_change()

        self.assertEqual(200, self.sol_p2.price_unit)
        self.assertEqual(180, self.sol_p2.price_unit_supplier)
        self.assertEqual(171, self.sol_p2.price_unit_alcyon)
        self.assertEqual(10, self.sol_p2.supplier_promotion)
        self.assertEqual(5, self.sol_p2.alcyon_discount)

        # There is 2 p2 in sale order so subtotal = 171 * 2
        self.assertEqual(342, self.sol_p2.price_subtotal)

        # Change supplier promotion
        self.sol_p2.supplier_promotion = 8.24
        self.sol_p2.onchange_promotion_discount()

        self.assertEqual(200, self.sol_p2.price_unit)
        self.assertEqual(183.52, self.sol_p2.price_unit_supplier)
        self.assertEqual(174.34, self.sol_p2.price_unit_alcyon)
        self.assertEqual(8.24, self.sol_p2.supplier_promotion)
        self.assertEqual(5, self.sol_p2.alcyon_discount)

        # There is 2 p2 in sale order so subtotal = 174.34 * 2
        self.assertEqual(348.68, self.sol_p2.price_subtotal)

        # Change alcyon discount
        self.sol_p2.alcyon_discount = 3.83
        self.sol_p2.onchange_promotion_discount()

        self.assertEqual(200, self.sol_p2.price_unit)
        self.assertEqual(183.52, self.sol_p2.price_unit_supplier)
        self.assertEqual(176.49, self.sol_p2.price_unit_alcyon)
        self.assertEqual(8.24, self.sol_p2.supplier_promotion)
        self.assertEqual(3.83, self.sol_p2.alcyon_discount)

        # There is 2 p2 in sale order so subtotal = 174.34 * 2
        self.assertEqual(352.98, self.sol_p2.price_subtotal)

        # Change both
        self.sol_p2.supplier_promotion = 20
        self.sol_p2.alcyon_discount = 10
        self.sol_p2.onchange_promotion_discount()

        self.assertEqual(200, self.sol_p2.price_unit)
        self.assertEqual(160, self.sol_p2.price_unit_supplier)
        self.assertEqual(144, self.sol_p2.price_unit_alcyon)
        self.assertEqual(20, self.sol_p2.supplier_promotion)
        self.assertEqual(10, self.sol_p2.alcyon_discount)

        # There is 2 p2 in sale order so subtotal = 174.34 * 2
        self.assertEqual(288, self.sol_p2.price_subtotal)

        # Change quantity
        self.sol_p2.product_uom_qty = 1

        self.assertEqual(200, self.sol_p2.price_unit)
        self.assertEqual(160, self.sol_p2.price_unit_supplier)
        self.assertEqual(144, self.sol_p2.price_unit_alcyon)
        self.assertEqual(20, self.sol_p2.supplier_promotion)
        self.assertEqual(10, self.sol_p2.alcyon_discount)

        self.assertEqual(144, self.sol_p2.price_subtotal)

        # Bug when only alcyon was filled
        # (And alcyon_discount should not be recompute)
        self.sol_p2.price_unit = 0.46
        self.sol_p2.supplier_promotion = 0
        self.sol_p2.alcyon_discount = 5
        self.sol_p2.onchange_promotion_discount()

        self.assertEqual(0.46, self.sol_p2.price_unit)
        self.assertEqual(0.46, self.sol_p2.price_unit_supplier)
        self.assertEqual(0.44, self.sol_p2.price_unit_alcyon)
        self.assertEqual(0, self.sol_p2.supplier_promotion)
        self.assertEqual(5, self.sol_p2.alcyon_discount)

        self.assertEqual(0.44, self.sol_p2.price_subtotal)

    def test_create_invoice(self):
        self.tax.amount = 20

        for line in self.sale.order_line:
            line.product_id_change()

        self.sale.action_confirm()

        invoices = self.sale.action_invoice_create(final=True)
        self.assertEqual(1, len(invoices))
        invoice = self.env['account.invoice'].browse(invoices[0])

        self.assertEqual(518.4, self.sale.amount_total)
        self.assertEqual(86.4, self.sale.amount_tax)

        self.assertEqual(518.4, invoice.amount_total)
        self.assertEqual(86.4, invoice.amount_tax)

        # Check lines
        line1 = invoice.invoice_line_ids.filtered(
            lambda l: l.product_id == self.p1
        )
        self.assertEqual(100, line1.price_unit)
        self.assertEqual(10, line1.supplier_promotion)
        self.assertEqual(0, line1.alcyon_discount)
        self.assertEqual(90, line1.price_subtotal)

        line2 = invoice.invoice_line_ids.filtered(
            lambda l: l.product_id == self.p2
        )
        self.assertEqual(200, line2.price_unit)
        self.assertEqual(10, line2.supplier_promotion)
        self.assertEqual(5, line2.alcyon_discount)
        self.assertEqual(342, line2.price_subtotal)

        # Check taxes
        self.assertEqual(1, len(invoice.tax_line_ids))
        self.assertEqual(86.4, invoice.tax_line_ids[0].amount)

    def test_coverage(self):
        """ Test special cases for coverage.
        """

        # Supplier promotion 100%
        self.promotion_pricelist_id.item_ids.percent_price = 100
        self.tax.amount = 20

        for line in self.sale.order_line:
            line.product_id_change()

        self.assertEqual(100, self.sol_p1.price_unit)
        self.assertEqual(0, self.sol_p1.price_unit_supplier)
        self.assertEqual(0, self.sol_p1.price_unit_alcyon)
        self.assertEqual(100, self.sol_p1.supplier_promotion)
        self.assertEqual(0, self.sol_p1.alcyon_discount)

        self.assertEqual(0, self.sol_p1.price_subtotal)
        self.assertEqual(0, self.sol_p1.price_tax)
        self.assertAlmostEqual(0, self.sol_p1.price_total)

        self.assertEqual(200, self.sol_p2.price_unit)
        self.assertEqual(0, self.sol_p2.price_unit_supplier)
        self.assertEqual(0, self.sol_p2.price_unit_alcyon)
        self.assertEqual(100, self.sol_p2.supplier_promotion)
        self.assertEqual(0, self.sol_p2.alcyon_discount)

        self.assertEqual(0, self.sol_p2.price_subtotal)
        self.assertEqual(0, self.sol_p2.price_tax)
        self.assertAlmostEqual(0, self.sol_p2.price_total)

        self.assertEqual(0, self.sale.amount_total)

    def test_commercial_fields(self):
        sub_partner = self.env['res.partner'].create({
            'parent_id': self.partner.id,
            'name': 'Unittest sub partner',
        })

        self.sale.write({
            'promotion_pricelist_id': False,
            'discount_pricelist_id': False,
            'partner_id': sub_partner.id,
        })

        self.sale.onchange_partner_id_discount_pricelist()
        self.assertEqual(
            self.promotion_pricelist_id, self.sale.promotion_pricelist_id
        )
        self.assertEqual(
            self.discount_pricelist_id, self.sale.discount_pricelist_id
        )
