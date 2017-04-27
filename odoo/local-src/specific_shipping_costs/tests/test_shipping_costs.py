# -*- coding: utf-8 -*-
# Copyright 2017 Julien Coux (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestShippingCosts(TransactionCase):

    def setUp(self):
        super(TestShippingCosts, self).setUp()

        self.sale_config_settings_model = self.env['sale.config.settings']

        self.partner = self.env['res.partner'].create({
            'name': 'Unittest partner',
        })

        self.tax = self.env["account.tax"].create({
            'name': 'Unittest tax',
            'price_include': False,
            'amount_type': 'percent',
            'amount': '0',
        })

        self.p1 = self.env['product.template'].create({
            'name': 'Unittest P1',
            'uom_id': self.ref('product.product_uom_unit'),
            'type': 'consu',
            'taxes_id': [(6, False, [self.tax.id])],
        })

        self.delivery_carrier_model = self.env['delivery.carrier']
        self.deliver_carrier_fixed = self.delivery_carrier_model.create({
            'name': 'shipping costs 10€',
            'delivery_type': 'fixed',
            'fixed_price': 10.0,
        })
        self.deliver_carrier_fixed.write({
            'taxes_id': [(6, False, [self.tax.id])],
        })
        self.deliver_carrier_on_invoice = self.delivery_carrier_model.create({
            'name': 'shipping costs on invoice',
            'delivery_type': 'fixed',
            'compute_shipping_costs_on_invoice': True,
            'fixed_price': 15.9,
            'free_if_more_than': True,
            'amount': 345.36,
        })
        self.deliver_carrier_on_invoice._compute_fixed_price()

    def test_01_deliver_carrier_fixed(self):
        sale = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'carrier_id': self.deliver_carrier_fixed.id,
            'order_line': [
                (0, 0, {
                    'name': self.p1.name,
                    'product_id': self.p1.product_variant_ids.id,
                    'product_uom': self.ref('product.product_uom_unit'),
                    'product_uom_qty': 1,
                    'price_unit': 200,
                }),
            ]
        })
        self.assertEqual(sale.amount_total, 200)
        sale.delivery_set()
        self.assertEqual(sale.amount_total, 200 + 10)
        sale.action_confirm()
        self.assertEqual(len(sale.picking_ids), 1)
        picking = sale.picking_ids
        picking.action_assign()
        picking.action_done()
        self.assertEqual(picking.state, 'done')
        sale.action_invoice_create()
        self.assertEqual(len(sale.invoice_ids), 1)
        invoice = sale.invoice_ids
        invoice.compute_shipping_costs()
        self.assertEqual(invoice.amount_total, 200 + 10)

    def test_02_deliver_carrier_on_invoice_with_delivery_cost(self):
        sale = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'carrier_id': self.deliver_carrier_on_invoice.id,
            'order_line': [
                (0, 0, {
                    'name': self.p1.name,
                    'product_id': self.p1.product_variant_ids.id,
                    'product_uom': self.ref('product.product_uom_unit'),
                    'product_uom_qty': 1,
                    'price_unit': 345.35,
                }),
            ]
        })
        self.assertEqual(sale.amount_total, 345.35)
        sale.action_confirm()
        self.assertEqual(len(sale.picking_ids), 1)
        picking = sale.picking_ids
        picking.action_assign()
        picking.action_done()
        self.assertEqual(picking.state, 'done')
        sale.action_invoice_create()
        self.assertEqual(len(sale.invoice_ids), 1)
        invoice = sale.invoice_ids
        invoice.compute_shipping_costs()
        self.assertEqual(invoice.amount_total, 345.35 + 15.9)

    def test_03_deliver_carrier_on_invoice_with_no_cost(self):
        sale = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'carrier_id': self.deliver_carrier_on_invoice.id,
            'order_line': [
                (0, 0, {
                    'name': self.p1.name,
                    'product_id': self.p1.product_variant_ids.id,
                    'product_uom': self.ref('product.product_uom_unit'),
                    'product_uom_qty': 1,
                    'price_unit': 345.36,
                }),
            ]
        })
        self.assertEqual(sale.amount_total, 345.36)
        sale.action_confirm()
        self.assertEqual(len(sale.picking_ids), 1)
        picking = sale.picking_ids
        picking.action_assign()
        picking.action_done()
        self.assertEqual(picking.state, 'done')
        sale.action_invoice_create()
        self.assertEqual(len(sale.invoice_ids), 1)
        invoice = sale.invoice_ids
        invoice.compute_shipping_costs()
        self.assertEqual(invoice.amount_total, 345.36)

    def test_04_deliver_carrier_on_invoice_with_delivery_cost_with_2_lines(
            self
    ):
        sale = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'carrier_id': self.deliver_carrier_on_invoice.id,
            'order_line': [
                (0, 0, {
                    'name': self.p1.name,
                    'product_id': self.p1.product_variant_ids.id,
                    'product_uom': self.ref('product.product_uom_unit'),
                    'product_uom_qty': 1,
                    'price_unit': 345.34,
                }),
                (0, 0, {
                    'name': self.p1.name,
                    'product_id': self.p1.product_variant_ids.id,
                    'product_uom': self.ref('product.product_uom_unit'),
                    'product_uom_qty': 1,
                    'price_unit': 0.01,
                }),
            ]
        })
        self.assertEqual(sale.amount_total, 345.35)
        sale.action_confirm()
        self.assertEqual(len(sale.picking_ids), 1)
        picking = sale.picking_ids
        picking.action_assign()
        picking.action_done()
        self.assertEqual(picking.state, 'done')
        sale.action_invoice_create()
        self.assertEqual(len(sale.invoice_ids), 1)
        invoice = sale.invoice_ids
        invoice.compute_shipping_costs()
        self.assertEqual(invoice.amount_total, 345.35 + 15.9)

    def test_05_deliver_carrier_on_invoice_with_no_cost_with_2_lines(self):
        sale = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'carrier_id': self.deliver_carrier_on_invoice.id,
            'order_line': [
                (0, 0, {
                    'name': self.p1.name,
                    'product_id': self.p1.product_variant_ids.id,
                    'product_uom': self.ref('product.product_uom_unit'),
                    'product_uom_qty': 1,
                    'price_unit': 345.35,
                }),
                (0, 0, {
                    'name': self.p1.name,
                    'product_id': self.p1.product_variant_ids.id,
                    'product_uom': self.ref('product.product_uom_unit'),
                    'product_uom_qty': 1,
                    'price_unit': 0.01,
                }),
            ]
        })
        self.assertEqual(sale.amount_total, 345.36)
        sale.action_confirm()
        self.assertEqual(len(sale.picking_ids), 1)
        picking = sale.picking_ids
        picking.action_assign()
        picking.action_done()
        self.assertEqual(picking.state, 'done')
        sale.action_invoice_create()
        self.assertEqual(len(sale.invoice_ids), 1)
        invoice = sale.invoice_ids
        invoice.compute_shipping_costs()
        self.assertEqual(invoice.amount_total, 345.36)

    def test_06_deliver_carrier_fixed_validate_invoice(self):
        sale = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'carrier_id': self.deliver_carrier_fixed.id,
            'order_line': [
                (0, 0, {
                    'name': self.p1.name,
                    'product_id': self.p1.product_variant_ids.id,
                    'product_uom': self.ref('product.product_uom_unit'),
                    'product_uom_qty': 1,
                    'price_unit': 200,
                }),
            ]
        })
        sale.delivery_set()
        sale.action_confirm()
        self.assertEqual(len(sale.picking_ids), 1)
        picking = sale.picking_ids
        picking.action_assign()
        picking.action_done()
        self.assertEqual(picking.state, 'done')
        sale.action_invoice_create()
        self.assertEqual(len(sale.invoice_ids), 1)
        invoice = sale.invoice_ids
        invoice.action_invoice_open()

    def test_07_deliver_carrier_on_invoice_with_delivery_cost_validate_invoice(
            self
    ):
        sale = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'carrier_id': self.deliver_carrier_on_invoice.id,
            'order_line': [
                (0, 0, {
                    'name': self.p1.name,
                    'product_id': self.p1.product_variant_ids.id,
                    'product_uom': self.ref('product.product_uom_unit'),
                    'product_uom_qty': 1,
                    'price_unit': 200,
                }),
            ]
        })
        sale.action_confirm()
        self.assertEqual(len(sale.picking_ids), 1)
        picking = sale.picking_ids
        picking.action_assign()
        picking.action_done()
        self.assertEqual(picking.state, 'done')
        sale.action_invoice_create()
        self.assertEqual(len(sale.invoice_ids), 1)
        invoice = sale.invoice_ids
        with self.assertRaises(Exception):
            invoice.action_invoice_open()
        invoice.compute_shipping_costs()
        invoice.action_invoice_open()
