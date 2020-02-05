# coding: utf-8
from odoo.addons.delivery_rounds.tests import common


class TestDeliveryRound(common.DeliveryRoundTestCase):
    """Common for fonctionnal tests cross module"""

    @classmethod
    def setUpClass(cls):
        super(TestDeliveryRound, cls).setUpClass()
        # part of the specific modules of Alcyon hard code the Stock location
        # to be ref('stock.stock_location_stock') -> we cannot use another
        # warehouse if we want to use these modules in our test (and we do)
        cls.warehouse_1 = cls.env.ref('stock.warehouse0')
        cls.warehouse_1.write(
            {
                'name': 'Test Warehouse',
                'reception_steps': 'one_step',
                'delivery_steps': 'pick_ship',
                'code': 'TST',
            }
        )
        cls.warehouse_1.pick_type_id.subcode = 'PICK'
        cls.warehouse_1.pick_type_id.groupbypartner = True
        cls.warehouse_1.out_type_id.groupbypartner = True
        cls.warehouse_1.out_type_id.create_invoice_on_transfer = True
        cls.loc_reserve = cls.env['stock.location'].create(
            {
                "name": "Reserve",
                "location_id": cls.warehouse_1.view_location_id.id,
                "usage": "internal",
                "kind": "reserve",
            }
        )
        inventory = cls.env['stock.inventory'].create(
            {'name': 'Test', 'product_id': cls.p1.id, 'filter': 'product'}
        )
        inventory.prepare_inventory()
        # clear stuff, as the inventory in common.setUpClass does not put the
        # products where we need them.
        # initial inventory:
        # * p1: 100 in stock, 100 in reserve
        # * p2:  10 in stock, 100 in reserve
        inventory.line_ids = False
        cls.env['stock.inventory.line'].create(
            {
                'inventory_id': inventory.id,
                'product_id': cls.p1.id,
                'product_uom_id': cls.p1.uom_id.id,
                'product_qty': 100,
                'location_id': cls.warehouse_1.lot_stock_id.id,
            }
        )
        # put 10 p2 in stock, and 100 in reserve
        cls.env['stock.inventory.line'].create(
            {
                'inventory_id': inventory.id,
                'product_id': cls.p2.id,
                'product_uom_id': cls.p2.uom_id.id,
                'product_qty': 10,
                'location_id': cls.warehouse_1.lot_stock_id.id,
            }
        )
        cls.env['stock.inventory.line'].create(
            {
                'inventory_id': inventory.id,
                'product_id': cls.p2.id,
                'product_uom_id': cls.p2.uom_id.id,
                'product_qty': 100,
                'location_id': cls.loc_reserve.id,
            }
        )
        inventory.action_done()

        # Create the delivery carrier for Alcyon
        cls.fee = 8.5
        cls.delivery_method = cls.env['delivery.carrier'].create(
            {
                'delivery_type': 'fixed',
                'fixed_price': cls.fee,
                'free_if_more_than': True,
                'amount': 125,
                'use_specific_cost_calculation': True,
                'name': 'Alcyon',
            }
        )
