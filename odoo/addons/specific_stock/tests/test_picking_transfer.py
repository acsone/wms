# -*- coding: utf-8 -*-
# Copyright 2016 Julien Coux (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase, at_install, post_install


class TestPickingTransfer(TransactionCase):
    def setUp(self):
        super(TestPickingTransfer, self).setUp()
        self.category_model = self.env['product.category']
        self.product_model = self.env['product.product']
        self.partner_model = self.env['res.partner']
        self.location_model = self.env['stock.location']
        self.stock_picking_model = self.env['stock.picking']
        self.stock_config_settings_model = self.env['stock.config.settings']

        settings = self.stock_config_settings_model.create(
            {'production_lot_base_date': 'life'}
        )
        settings.execute()

        self.category = self.category_model.create(
            {
                'name': 'Unittest Categ1',
                'use_time': 1,
                'life_time': 2,
                'alert_time': 3,
                'removal_time': 4,
            }
        )

        self.product = self.product_model.create(
            {
                'name': 'Unittest P1',
                'uom_id': self.ref('product.product_uom_unit'),
                'categ_id': self.category.id,
                'tracking': 'lot',
            }
        )

        self.supplier = self.partner_model.create(
            {'name': 'Unittest supplier', 'ref': '892374928374234'}
        )

        self.supplier_location = self.location_model.browse(
            self.ref('stock.stock_location_suppliers')
        )
        self.stock_location = self.location_model.browse(
            self.ref('stock.stock_location_stock')
        )
        self.grn = self.env['stock.grn'].create(
            {'carrier_id': self.supplier.id}
        )

    @post_install(True)
    @at_install(False)
    def test_1_picking_transfer(self):
        picking = self.stock_picking_model.create(
            {
                'picking_type_id': self.ref('stock.picking_type_in'),
                'location_id': self.supplier_location.id,
                'location_dest_id': self.stock_location.id,
                'to_process_quant_expired': True,
                'move_lines': [
                    (
                        0,
                        0,
                        {
                            'name': 'a move',
                            'product_id': self.product.id,
                            'product_uom_qty': 1,
                            'product_uom': self.product.uom_id.id,
                            'location_id': self.supplier_location.id,
                            'location_dest_id': self.stock_location.id,
                        },
                    )
                ],
                'grn_id': self.grn.id,
            }
        )
        picking.action_assign()
        pack_operation = picking.pack_operation_product_ids
        pack_operation.write(
            {
                'pack_lot_ids': [
                    (
                        0,
                        0,
                        {
                            'life_date': '2017-01-02 10:00:00',
                            'lot_name': '20170102',
                            'qty': 1,
                        },
                    )
                ],
                'qty_done': 1,
            }
        )
        picking.do_transfer()

        quants = self.env['stock.quant'].search(
            [('product_id', '=', self.product.id)]
        )
        self.assertEqual(len(quants), 1)
        self.assertEqual(quants[0].qty, 1)
        self.assertEqual(quants[0].removal_date, '2017-01-04 10:00:00')

        lot = quants[0].lot_id
        self.assertEqual(lot.name, '20170102')
        self.assertEqual(lot.use_date, '2017-01-01 10:00:00')
        self.assertEqual(lot.life_date, '2017-01-02 10:00:00')
        self.assertEqual(lot.alert_date, '2017-01-03 10:00:00')
        self.assertEqual(lot.removal_date, '2017-01-04 10:00:00')
