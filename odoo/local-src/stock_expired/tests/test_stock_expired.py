# -*- coding: utf-8 -*-
# Copyright 2016 Julien Coux (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime

from odoo import fields, tools
from odoo.tests.common import TransactionCase, at_install, post_install


class TestStockExpired(TransactionCase):
    def setUp(self):
        super(TestStockExpired, self).setUp()

        self.quant_model = self.env['stock.quant']
        self.picking_model = self.env['stock.picking']
        self.location_model = self.env['stock.location']
        self.product_model = self.env['product.product']
        self.production_lot_model = self.env['stock.production.lot']
        self.inventory_model = self.env['stock.inventory']
        self.inventory_line_model = self.env['stock.inventory.line']
        self.mail_message_model = self.env['mail.message']

        self.stock_location = self.location_model.browse(
            self.ref('stock.stock_location_stock')
        )
        self.customer_location = self.location_model.browse(
            self.ref('stock.stock_location_customers')
        )

        self.product = self.product_model.create(
            {'name': 'Unittest product', 'type': 'product'}
        )
        self.production_lot = self.production_lot_model.create(
            {'name': '000001', 'product_id': self.product.id}
        )

    def _add_product_qty(self, product, production_lot, quantity):
        self.inventory = self.inventory_model.create(
            {
                'name': 'Unittest Inventory',
                'location_id': self.stock_location.id,
                'filter': 'partial',
            }
        )
        self.inventory.prepare_inventory()

        self.inventory_line_model.create(
            {
                'inventory_id': self.inventory.id,
                'product_id': product.id,
                'location_id': self.stock_location.id,
                'product_qty': quantity,
                'prod_lot_id': production_lot.id,
            }
        )
        self.inventory.action_done()

    def _create_out_picking(self, product, quantity):
        return self.picking_model.create(
            {
                'picking_type_id': self.ref('stock.picking_type_out'),
                'location_id': self.stock_location.id,
                'location_dest_id': self.customer_location.id,
                'move_lines': [
                    (
                        0,
                        0,
                        {
                            'name': 'a move',
                            'product_id': product.id,
                            'product_uom_qty': quantity,
                            'product_uom': self.product.uom_id.id,
                            'location_id': self.stock_location.id,
                            'location_dest_id': self.customer_location.id,
                        },
                    )
                ],
            }
        )

    @post_install(True)
    @at_install(False)
    def test_1_qty_on_excess(self):
        self._add_product_qty(self.product, self.production_lot, 5)

        picking_out = self._create_out_picking(self.product, 8)

        picking_out.action_assign()
        self.assertEqual(picking_out.state, 'partially_available')

    @post_install(True)
    @at_install(False)
    def test_2_qty_available(self):
        self._add_product_qty(self.product, self.production_lot, 5)

        picking_out = self._create_out_picking(self.product, 5)
        picking_out.action_assign()
        self.assertEqual(picking_out.state, 'assigned')

    @post_install(True)
    @at_install(False)
    def test_3_qty_expired(self):
        self.production_lot.removal_date = '2016-12-08 12:00:00'
        self._add_product_qty(self.product, self.production_lot, 5)

        picking_out = self._create_out_picking(self.product, 5)
        picking_out.action_assign()
        self.assertEqual(picking_out.state, 'confirmed')

        # We now ignore quants expiration
        self.stock_location.ignore_quants_expiration = True

        picking_out.action_assign()
        self.assertEqual(picking_out.state, 'assigned')

    @post_install(True)
    @at_install(False)
    def test_4_process_quant_expired(self):
        product_ok_1 = self.product_model.create(
            {'name': 'Unittest product', 'type': 'product'}
        )
        production_lot_ok_1 = self.production_lot_model.create(
            {'name': '000001', 'product_id': product_ok_1.id}
        )
        product_ko_1 = self.product_model.create(
            {'name': 'Unittest product', 'type': 'product'}
        )
        production_lot_ko_1 = self.production_lot_model.create(
            {
                'name': '000001',
                'product_id': product_ko_1.id,
                'removal_date': '2016-12-08 12:00:00',
            }
        )
        product_ko_2 = self.product_model.create(
            {'name': 'Unittest product', 'type': 'product'}
        )
        production_lot_ko_2 = self.production_lot_model.create(
            {
                'name': '000001',
                'product_id': product_ko_2.id,
                'removal_date': '2016-12-08 12:00:00',
            }
        )
        self._add_product_qty(product_ok_1, production_lot_ok_1, 5)
        self._add_product_qty(product_ko_1, production_lot_ko_1, 3)
        self._add_product_qty(product_ko_2, production_lot_ko_2, 4)

        self.assertEqual(product_ok_1.qty_available, 5)
        self.assertEqual(product_ok_1.virtual_available, 5)

        self.assertEqual(product_ko_1.qty_available, 3)
        self.assertEqual(product_ko_1.virtual_available, 3)

        self.assertEqual(product_ko_2.qty_available, 4)
        self.assertEqual(product_ko_2.virtual_available, 4)

        now = datetime.strftime(
            fields.datetime.now(), tools.DEFAULT_SERVER_DATETIME_FORMAT
        )

        domain = [
            ('removal_date', '<=', now),
            ('location_id.usage', '=', 'internal'),
            ('location_id.ignore_quants_expiration', '=', False),
        ]
        # First test: we ignore quants expiration
        # Second test: we don't ignore quants expiration
        for ignore in [True, False]:
            self.stock_location.ignore_quants_expiration = ignore

            quants_expired = self.quant_model.search(domain)
            self.assertEqual(
                len(quants_expired),
                0 if ignore else 2,  # Quants expiration is ignored
            )

            self.quant_model.process_quant_expired()

            self.assertEqual(product_ok_1.qty_available, 5)
            self.assertEqual(product_ok_1.virtual_available, 5)

            self.assertEqual(product_ko_1.qty_available, 3)
            self.assertEqual(
                product_ko_1.virtual_available,
                3 if ignore else 0,  # Quants expiration is ignored
            )

            self.assertEqual(product_ko_2.qty_available, 4)
            self.assertEqual(
                product_ko_2.virtual_available,
                4 if ignore else 0,  # Quants expiration is ignored
            )
        # We continue tests with second test: don't ignore quants expiration

        scrapped_location_id = self.ref('stock.stock_location_scrapped')
        picking = self.picking_model.search(
            [('location_dest_id', '=', scrapped_location_id)]
        )
        self.assertListEqual(
            sorted(picking.mapped('move_lines.reserved_quant_ids').ids),
            sorted(quants_expired.ids),
        )
        picking = picking.with_context(
            params={'model': 'stock.picking', 'id': picking.id}
        )
        picking.action_assign()
        picking.action_done()
        for quant_expired in quants_expired:
            self.assertEqual(
                quant_expired.location_id.id, scrapped_location_id
            )

    @post_install(True)
    @at_install(False)
    def test_5_alert_quant_expired(self):
        # This test only check if alert mail is created,
        # but not the content of the mail
        self.quant_model.alert_quant_expired()
        mail_messages = self.mail_message_model.search(
            [('model', '=', 'stock.quant')]
        )
        self.assertEqual(len(mail_messages), 0)

        product_ok_1 = self.product_model.create(
            {'name': 'Unittest product', 'type': 'product'}
        )
        production_lot_ok_1 = self.production_lot_model.create(
            {'name': '000001', 'product_id': product_ok_1.id}
        )
        self._add_product_qty(product_ok_1, production_lot_ok_1, 5)

        self.quant_model.alert_quant_expired()
        mail_messages = self.mail_message_model.search(
            [('model', '=', 'stock.quant')]
        )
        self.assertEqual(len(mail_messages), 0)

        product_ko_1 = self.product_model.create(
            {'name': 'Unittest product', 'type': 'product'}
        )
        production_lot_ko_1 = self.production_lot_model.create(
            {
                'name': '000001',
                'product_id': product_ko_1.id,
                'alert_date': '2016-12-08 12:00:00',
            }
        )
        self._add_product_qty(product_ko_1, production_lot_ko_1, 3)
        product_ko_2 = self.product_model.create(
            {'name': 'Unittest product', 'type': 'product'}
        )
        production_lot_ko_2 = self.production_lot_model.create(
            {
                'name': '000001',
                'product_id': product_ko_2.id,
                'alert_date': '2016-12-08 12:00:00',
            }
        )
        self._add_product_qty(product_ko_2, production_lot_ko_2, 4)

        # First test: we ignore quants expiration
        # Second test: we don't ignore quants expiration
        for ignore in [True, False]:
            self.stock_location.ignore_quants_expiration = ignore

            self.quant_model.alert_quant_expired()
            mail_messages = self.mail_message_model.search(
                [('model', '=', 'stock.quant')]
            )
            self.assertEqual(
                len(mail_messages),
                0 if ignore else 1,  # Quants expiration is ignored
            )
            if not ignore:
                self.assertEqual(mail_messages[0].subject, 'Quants on alert')
