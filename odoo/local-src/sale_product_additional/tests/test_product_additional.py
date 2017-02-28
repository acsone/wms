# -*- coding: utf-8 -*-
# Copyright 2016 Julien Coux (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestProductAdditional(TransactionCase):

    def setUp(self):
        super(TestProductAdditional, self).setUp()

        self.tax = self.env["account.tax"].create({
            'name': 'Unittest tax',
            'price_include': False,
            'amount_type': 'percent',
            'amount': '0',
        })

        self.add_p1 = self.env['product.template'].create({
            'name': 'Unittest additional P1',
            'uom_id': self.ref('product.product_uom_unit'),
            'price': 50,
            'taxes_id': [(6, False, [self.tax.id])],
            'description_sale': 'Unittest additional P1 for sale',
        })

        self.p1 = self.env['product.template'].create({
            'name': 'Unittest P1',
            'uom_id': self.ref('product.product_uom_unit'),
            'additional_product_ids': [
                (0, 0, {
                    'original_quantity': 1,
                    'product_id': self.add_p1.id,
                    'quantity': 1,
                    'calculation_method': 'once',
                    'is_free': False,
                    'position_on_sale': 'just_after',
                }),
            ],
            'price': 150,
            'taxes_id': [(6, False, [self.tax.id])],
        })

        self.p2 = self.env['product.template'].create({
            'name': 'Unittest P2',
            'uom_id': self.ref('product.product_uom_unit'),
        })

        self.p3 = self.env['product.template'].create({
            'name': 'Unittest P3',
            'uom_id': self.ref('product.product_uom_unit'),
            'additional_product_ids': [
                (0, 0, {
                    'original_quantity': 1,
                    'product_id': self.add_p1.id,
                    'quantity': 4,
                    'calculation_method': 'once',
                    'is_free': True,
                    'position_on_sale': 'at_end',
                }),
            ],
            'price': 250,
            'taxes_id': [(6, False, [self.tax.id])],
        })

        self.p4 = self.env['product.template'].create({
            'name': 'Unittest P4',
            'uom_id': self.ref('product.product_uom_unit'),
            'additional_product_ids': [
                (0, 0, {
                    'original_quantity': 10,
                    'product_id': self.add_p1.id,
                    'quantity': 1,
                    'calculation_method': 'proportional',
                    'is_free': False,
                    'position_on_sale': 'just_after',
                }),
            ]
        })

        self.partner = self.env['res.partner'].create({
            'name': 'Unittest partner',
        })

    def test_1_basic(self):
        self.sale = self.env['sale.order'].new({
            'partner_id': self.partner.id,
        })

        self.sale.update({
            'order_line_original': [
                (0, 0, {
                    'name': self.p1.name,
                    'product_id': self.p1.product_variant_ids.id,
                    'product_uom': self.ref('product.product_uom_unit'),
                    'product_uom_qty': 1,
                    'sequence': 1,
                }),
            ]
        })

        self.sale._onchange_order_line_original()

        self.assertEqual(len(self.sale.order_line), 2)

    def test_2_position_on_sale_just_after(self):
        self.sale = self.env['sale.order'].new({
            'partner_id': self.partner.id,
        })
        self.sale.update({
            'order_line_original': [
                (0, 0, {
                    'name': self.p1.name,
                    'product_id': self.p1.product_variant_ids.id,
                    'product_uom': self.ref('product.product_uom_unit'),
                    'product_uom_qty': 1,
                    'sequence': 1,
                }),
                (0, 0, {
                    'name': self.p2.name,
                    'product_id': self.p2.product_variant_ids.id,
                    'product_uom': self.ref('product.product_uom_unit'),
                    'product_uom_qty': 1,
                    'sequence': 2,
                }),
            ]
        })

        self.sale._onchange_order_line_original()

        self.assertEqual(len(self.sale.order_line), 3)

        lines = self.sale.order_line.sorted(key=lambda l: l.sequence)

        self.assertEqual(lines[0].product_id,
                         self.p1.product_variant_ids[0])

        self.assertEqual(lines[1].product_id,
                         self.add_p1.product_variant_ids[0])

        self.assertEqual(lines[2].product_id,
                         self.p2.product_variant_ids[0])

    def test_3_position_on_sale_at_end(self):
        self.sale = self.env['sale.order'].new({
            'partner_id': self.partner.id,
        })
        self.sale.update({
            'order_line_original': [
                (0, 0, {
                    'name': self.p3.name,
                    'product_id': self.p3.product_variant_ids.id,
                    'product_uom': self.ref('product.product_uom_unit'),
                    'product_uom_qty': 1,
                    'sequence': 1,
                }),
                (0, 0, {
                    'name': self.p2.name,
                    'product_id': self.p2.product_variant_ids.id,
                    'product_uom': self.ref('product.product_uom_unit'),
                    'product_uom_qty': 1,
                    'sequence': 2,
                }),
            ]
        })

        self.sale._onchange_order_line_original()

        self.assertEqual(len(self.sale.order_line), 3)

        lines = self.sale.order_line.sorted(key=lambda l: l.sequence)

        self.assertEqual(lines[0].product_id,
                         self.p3.product_variant_ids[0])

        self.assertEqual(lines[1].product_id,
                         self.p2.product_variant_ids[0])

        self.assertEqual(lines[2].product_id,
                         self.add_p1.product_variant_ids[0])

    def test_4_calculation_method_once(self):
        self.sale = self.env['sale.order'].new({
            'partner_id': self.partner.id,
        })

        self.sale.update({
            'order_line_original': [
                (0, 0, {
                    'name': self.p1.name,
                    'product_id': self.p1.product_variant_ids.id,
                    'product_uom': self.ref('product.product_uom_unit'),
                    'product_uom_qty': 1,
                    'sequence': 1,
                }),
            ]
        })

        self.sale._onchange_order_line_original()

        self.assertEqual(len(self.sale.order_line), 2)

        lines = self.sale.order_line.sorted(key=lambda l: l.sequence)

        self.assertEqual(lines[0].product_uom_qty, 1)
        self.assertEqual(lines[1].product_uom_qty, 1)

        self.sale.update({
            'order_line_original': [
                (0, 0, {
                    'name': self.p1.name,
                    'product_id': self.p1.product_variant_ids.id,
                    'product_uom': self.ref('product.product_uom_unit'),
                    'product_uom_qty': 100,
                    'sequence': 1,
                }),
            ]
        })

        self.sale._onchange_order_line_original()

        self.assertEqual(len(self.sale.order_line), 2)

        lines = self.sale.order_line.sorted(key=lambda l: l.sequence)

        self.assertEqual(lines[0].product_uom_qty, 100)
        self.assertEqual(lines[1].product_uom_qty, 1)

    def test_5_calculation_method_proportional(self):
        self.sale = self.env['sale.order'].new({
            'partner_id': self.partner.id,
        })

        self.sale.update({
            'order_line_original': [
                (0, 0, {
                    'name': self.p4.name,
                    'product_id': self.p4.product_variant_ids.id,
                    'product_uom': self.ref('product.product_uom_unit'),
                    'product_uom_qty': 1,
                    'sequence': 1,
                }),
            ]
        })

        self.sale._onchange_order_line_original()

        self.assertEqual(len(self.sale.order_line), 1)

        lines = self.sale.order_line.sorted(key=lambda l: l.sequence)

        self.assertEqual(lines[0].product_uom_qty, 1)

        self.sale.update({
            'order_line_original': [
                (0, 0, {
                    'name': self.p4.name,
                    'product_id': self.p4.product_variant_ids.id,
                    'product_uom': self.ref('product.product_uom_unit'),
                    'product_uom_qty': 100,
                    'sequence': 1,
                }),
            ]
        })

        self.sale._onchange_order_line_original()

        self.assertEqual(len(self.sale.order_line), 2)

        lines = self.sale.order_line.sorted(key=lambda l: l.sequence)

        self.assertEqual(lines[0].product_uom_qty, 100)
        self.assertEqual(lines[1].product_uom_qty, 10)

        self.sale.update({
            'order_line_original': [
                (0, 0, {
                    'name': self.p4.name,
                    'product_id': self.p4.product_variant_ids.id,
                    'product_uom': self.ref('product.product_uom_unit'),
                    'product_uom_qty': 109,
                    'sequence': 1,
                }),
            ]
        })

        self.sale._onchange_order_line_original()

        self.assertEqual(len(self.sale.order_line), 2)

        lines = self.sale.order_line.sorted(key=lambda l: l.sequence)

        self.assertEqual(lines[0].product_uom_qty, 109)
        self.assertEqual(lines[1].product_uom_qty, 10)

    def test_6_is_free(self):
        self.sale = self.env['sale.order'].new({
            'partner_id': self.partner.id,
        })
        self.sale.update({
            'order_line_original': [
                (0, 0, {
                    'name': self.p1.name,
                    'product_id': self.p1.product_variant_ids.id,
                    'product_uom': self.ref('product.product_uom_unit'),
                    'product_uom_qty': 1,
                    'sequence': 1,
                }),
                (0, 0, {
                    'name': self.p3.name,
                    'product_id': self.p3.product_variant_ids.id,
                    'product_uom': self.ref('product.product_uom_unit'),
                    'product_uom_qty': 1,
                    'sequence': 2,
                }),
            ]
        })

        for line in self.sale.order_line_original:
            line.product_id_change()
        self.sale._onchange_order_line_original()

        self.assertEqual(len(self.sale.order_line), 4)

        lines = self.sale.order_line.sorted(key=lambda l: l.sequence)

        self.assertEqual(lines[0].price_unit, self.p1.price)
        self.assertEqual(lines[1].price_unit, self.add_p1.price)
        self.assertEqual(lines[2].price_unit, self.p3.price)
        self.assertEqual(lines[3].price_unit, 0)

    def test_7_quantity(self):
        self.sale = self.env['sale.order'].new({
            'partner_id': self.partner.id,
        })
        self.sale.update({
            'order_line_original': [
                (0, 0, {
                    'name': self.p3.name,
                    'product_id': self.p3.product_variant_ids.id,
                    'product_uom': self.ref('product.product_uom_unit'),
                    'product_uom_qty': 1,
                    'sequence': 1,
                }),
            ]
        })

        for line in self.sale.order_line_original:
            line.product_id_change()
        self.sale._onchange_order_line_original()

        self.assertEqual(len(self.sale.order_line), 2)

        lines = self.sale.order_line.sorted(key=lambda l: l.sequence)

        self.assertEqual(lines[0].product_uom_qty, 1)
        self.assertEqual(lines[1].product_uom_qty, 4)

    def test_8_constraints(self):
        values = {
            'name': 'Unittest P1',
            'uom_id': self.ref('product.product_uom_unit'),
            'additional_product_ids': [
                (0, 0, {
                    'original_quantity': 0,
                    'product_id': self.add_p1.id,
                    'quantity': 1,
                    'calculation_method': 'once',
                    'is_free': False,
                    'position_on_sale': 'just_after',
                }),
            ],
        }
        with self.assertRaises(Exception):
            self.env['product.template'].create(values)

        values['additional_product_ids'][0][2]['original_quantity'] = 1
        values['additional_product_ids'][0][2]['quantity'] = 0

        with self.assertRaises(Exception):
            self.env['product.template'].create(values)
