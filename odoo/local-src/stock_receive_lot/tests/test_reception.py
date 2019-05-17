# -*- coding: utf-8 -*-
# Copyright 2017 Jacques-Etienne Baudoux <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase, at_install, post_install


class TestReception(TransactionCase):
    def setUp(self):
        super(TestReception, self).setUp()
        self.category_model = self.env['product.category']
        self.product_model = self.env['product.product']
        self.partner_model = self.env['res.partner']

        # force parent_left/right computation
        self.location_model = self.env['stock.location']
        # self.location_model.pool._init = False

        self.stock_picking_model = self.env['stock.picking']
        self.stock_reception_wizard = self.env['stock.pack.operation.lot.add']

        self.products = [
            self.product_model.create(d)
            for d in [
                {
                    'name': 'Unittest Reception P1',
                    'uom_id': self.ref('product.product_uom_unit'),
                    'tracking': 'lot',
                },
                {
                    'name': 'Unittest Reception P2',
                    'uom_id': self.ref('product.product_uom_unit'),
                    'tracking': 'lot',
                },
            ]
        ]

        self.supplier = self.partner_model.create(
            {'name': 'Unittest supplier', 'ref': '839737475756467'}
        )

        self.supplier_location = self.location_model.browse(
            self.ref('stock.stock_location_suppliers')
        )
        self.stock_location = self.location_model.browse(
            self.ref('stock.stock_location_stock')
        )
        self.reception_location = self.location_model.create(
            {
                'name': 'reception',
                'location_id': self.stock_location.id,
                'usage': 'internal',
                'act_as_view': True,
            }
        )
        self.bin1 = self.location_model.create(
            {
                'name': 'bin1',
                'location_id': self.reception_location.id,
                'usage': 'internal',
            }
        )
        self.bin2 = self.location_model.create(
            {
                'name': 'bin2',
                'location_id': self.reception_location.id,
                'usage': 'internal',
            }
        )
        picking = self.stock_picking_model.create(
            {
                'picking_type_id': self.ref('stock.picking_type_in'),
                'location_id': self.supplier_location.id,
                'location_dest_id': self.reception_location.id,
                'move_lines': [
                    (
                        0,
                        0,
                        {
                            'name': 'move 1',
                            'product_id': product.id,
                            'product_uom_qty': 5,
                            'product_uom': product.uom_id.id,
                            'location_id': self.supplier_location.id,
                            'location_dest_id': self.reception_location.id,
                        },
                    )
                    for product in self.products
                ],
            }
        )
        picking = picking.with_context(test_mode=1)
        picking.action_assign()
        self.picking = picking

    @post_install(True)
    @at_install(False)
    def test_receive_on_view(self):
        picking = self.picking

        # launch wizard
        wiz = self.stock_reception_wizard.with_context(
            default_life_date_allowed=True
        ).new({'picking_id': picking.id})

        op1 = picking.pack_operation_product_ids[0]
        op2 = picking.pack_operation_product_ids[1]

        # select operation
        wiz.operation_id = op1
        wiz._onchange_operation_id()
        self.assertEqual(wiz.remaining_qty, 5)

        # select destination - it must be manually set
        self.assertEqual(wiz.location_dest_id.id, False)
        wiz.location_dest_id = self.bin1.id

        # receive first lot
        self.assertEqual(wiz.lot_required, 1)
        wiz.lot_name = 'Unittest Reception L1'
        wiz.life_date = '2030-01-01 10:00:00'
        wiz.qty = 3

        # go to next lot
        wiz = wiz.create(wiz._convert_to_write(wiz._cache))
        wiz.button_nextlot()
        self.assertEqual(wiz.operation_id, op1)
        self.assertEqual(wiz.remaining_qty, 2)
        self.assertEqual(wiz.location_dest_id, self.bin1)

        # receive second lot
        self.assertEqual(wiz.lot_required, 1)
        wiz.lot_name = 'Unittest Reception L2'
        wiz.life_date = '2030-01-01 10:00:00'
        wiz.qty = 1

        # go to next lot
        wiz.button_nextlot()
        self.assertEqual(wiz.operation_id, op1)
        self.assertEqual(wiz.remaining_qty, 1)
        self.assertEqual(wiz.location_dest_id, self.bin1)

        # receive again first lot
        self.assertEqual(wiz.lot_required, 1)
        wiz.lot_name = 'Unittest Reception L1'
        wiz.life_date = '2030-01-01 10:00:00'
        wiz.qty = 1

        # go to next operation
        wiz.button_nextop()
        self.assertEqual(wiz.operation_id.id, False)
        self.assertEqual(wiz.lot_name, False)
        self.assertEqual(wiz.life_date, False)
        self.assertEqual(wiz.qty, False)

        # select operation
        wiz.operation_id = op2
        wiz._onchange_operation_id()
        self.assertEqual(wiz.remaining_qty, 5)
        self.assertEqual(wiz.location_dest_id, self.bin1)

        # receive lot
        self.assertEqual(wiz.lot_required, 1)
        wiz.lot_name = 'Unittest Reception L3'
        wiz.life_date = '2030-01-01 10:00:00'
        wiz.qty = 5

        # go to next operation
        wiz.button_nextop()

        # validate
        picking.with_context(test_mode=True).do_transfer()
        self.assertEqual(picking.state, 'done')
        self.assertEqual(len(picking.move_lines), len(self.products))
        self.assertEqual(
            len(picking.pack_operation_product_ids), len(self.products)
        )

    @post_install(True)
    @at_install(False)
    def test_receive_on_bins(self):
        picking = self.picking
        # launch wizard
        wiz = self.stock_reception_wizard.with_context(
            default_life_date_allowed=True
        ).new({'picking_id': picking.id})

        op1 = picking.pack_operation_product_ids[0]
        op2 = picking.pack_operation_product_ids[1]

        # Simulate putaway to bin1 and bin2
        op1.location_dest_id = self.bin1
        op2.location_dest_id = self.bin2

        # select operation
        wiz.operation_id = op1
        wiz._onchange_operation_id()
        self.assertEqual(wiz.remaining_qty, 5)

        # destination is already pre-selected
        self.assertEqual(wiz.location_dest_id, self.bin1)

        # change operation
        wiz.operation_id = op2
        wiz._onchange_operation_id()
        self.assertEqual(wiz.remaining_qty, 5)

        # destination has changed
        self.assertEqual(wiz.location_dest_id, self.bin2)

        # receive a lot
        self.assertEqual(wiz.lot_required, 1)
        wiz.lot_name = 'Unittest Reception L1'
        wiz.life_date = '2030-01-01 10:00:00'
        wiz.qty = 1

        # go to next operation
        wiz.button_nextop()
        self.assertEqual(wiz.operation_id.id, False)
        self.assertEqual(wiz.lot_name, False)
        self.assertEqual(wiz.life_date, False)
        self.assertEqual(wiz.qty, False)

        # select operation
        wiz.operation_id = op1
        wiz._onchange_operation_id()
        self.assertEqual(wiz.remaining_qty, 5)

        # destination is already pre-selected
        self.assertEqual(wiz.location_dest_id, self.bin1)
