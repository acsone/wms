# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo.tests.common import TransactionCase


class TestStockDeliveryNote(TransactionCase):

    def setUp(self):
        super(TestStockDeliveryNote, self).setUp()

        # Create a sale tax
        self.tax = self.env['account.tax'].create({
            'tax_group_id': self.env.ref('account.tax_group_taxes').id,
            'amount': 6,
            'name': 'test_tax',
        })
        # Create a couple of products
        self.p1 = self.env['product.product'].create({
            'name': 'Unittest P1',
            'default_code': '5173360',
            'uom_id': self.ref('product.product_uom_unit'),
            'type': 'consu',
        })
        self.p2 = self.env['product.product'].create({
            'name': 'Unittest P2',
            'uom_id': self.ref('product.product_uom_unit'),
            'type': 'product',
        })
        self.p3 = self.env['product.product'].create({
            'name': 'Unittest P3',
            'uom_id': self.ref('product.product_uom_unit'),
            'type': 'product',
        })
        # Add some stock for p1 and p2
        inventory = self.env['stock.inventory'].create({
            'name': 'Test',
            'location_id': self.env.ref('stock.stock_location_stock').id,
            'filter': 'partial'})
        inventory.prepare_inventory()
        self.env['stock.inventory.line'].create({
            'inventory_id': inventory.id,
            'product_id': self.p1.id,
            'product_uom_id': self.ref('product.product_uom_unit'),
            'product_qty': 100,
            'location_id': self.env.ref('stock.stock_location_stock').id
            })
        inventory.action_done()
        inventory = self.env['stock.inventory'].create({
            'name': 'Test',
            'location_id': self.env.ref('stock.stock_location_stock').id,
            'filter': 'partial'})
        inventory.prepare_inventory()
        self.env['stock.inventory.line'].create({
            'inventory_id': inventory.id,
            'product_id': self.p2.id,
            'product_uom_id': self.ref('product.product_uom_unit'),
            'product_qty': 100,
            'location_id': self.env.ref('stock.stock_location_stock').id
            })
        inventory.action_done()
        # Create the customer
        self.partner = self.env['res.partner'].create({
            'title': self.env.ref('base.res_partner_title_prof').id,
            'name':  'HOENS OLIVIERé',
            'email': 'tester@pytest.com',
            'street':  'Rue Polisart 2 A',
            'zip': '5300',
            'city': 'ANDENNE',
            'country_id': self.env.ref('base.be').id,
        })
        self.destination = self.env.ref('stock.stock_location_customers')
        self.so = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'suite_name': '123454321',
            'order_line': [
                (0, 0, {
                    'name': self.p1.name,
                    'product_id': self.p1.id,
                    'product_uom': self.ref('product.product_uom_unit'),
                    'product_uom_qty': 10,
                    'price_unit': 50,
                    'tax_id': [(4, self.tax.id, False)],
                }),
            ]
        })
        self.so.action_confirm()
        self.picking = self.so.picking_ids
        self.picking.action_assign()
        pack_operation = self.picking.pack_operation_product_ids
        pack_operation.write({
            'pack_lot_ids': [
                (0, 0, {
                    'life_date': '2017-01-31 10:00:00',
                    'lot_name': '20170102',
                    'qty': 10,
                })
            ],
            'qty_done': 10,
        })
        self.picking.do_new_transfer()

    def test_creation_note_on_validate_picking(self):
        """Check that the csv document is in the store."""
        attachments = self.env['ir.attachment'].search([
            ('res_id', '=', self.picking.id)])
        self.assertEqual(len(attachments), 1)

    def test_delivery_note(self):
        """Check the format of the csv document"""
        tax_amount = ','.join(str(self.tax.amount).split('.'))
        expected = [
            [self.picking.id, 'tester@pytest.com'],
            [u'Prof. HOENS OLIVIERé', 'Rue Polisart 2 A',
             '5300 ANDENNE', self.env.ref('base.be').name],
            ['5173360', self.p1.name, '10,000', '50,00', '50,00',
             tax_amount, '20170102', '31-01-2017', '123454321'],
        ]
        lines = self.picking._generate_delivery_note()
        self.assertEqual(lines, expected)
