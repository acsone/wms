# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from contextlib import contextmanager

import mock
from odoo.tests.common import SavepointCase


class DeliveryRoundTestCase(SavepointCase):
    @contextmanager
    def mock_with_delay(self):
        with mock.patch(
            'odoo.addons.queue_job.models.base.DelayableRecordset',
            name='DelayableRecordset',
            spec=True,
        ) as delayable_cls:
            # prepare the mocks
            delayable = mock.MagicMock(name='DelayableBinding')
            delayable_cls.return_value = delayable
            yield delayable_cls, delayable

    @classmethod
    def setUpClass(cls):
        super(DeliveryRoundTestCase, cls).setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.partner1 = cls.env['res.partner'].create(
            {'name': 'Unittest partner', 'ref': '12344566777878'}
        )
        cls.partner2 = cls.env['res.partner'].create(
            {'name': 'Unittest partner', 'ref': '12344566777879'}
        )
        cls.partner3 = cls.env['res.partner'].create(
            {'name': 'Unittest partner', 'ref': '12344566777874'}
        )
        cls.p1 = cls.env['product.product'].create(
            {
                'name': 'Unittest P1',
                'uom_id': cls.env.ref('product.product_uom_unit').id,
                'type': 'product',
                'weight': 10.0,
            }
        )
        cls.p2 = cls.env['product.product'].create(
            {
                'name': 'Unittest P2',
                'uom_id': cls.env.ref('product.product_uom_unit').id,
                'type': 'product',
                'weight': 20.0,
            }
        )

        cls.delivery_template = cls.env['round.template'].create(
            {'name': 'Unittest delivery template'}
        )

        cls.delivery_round_1 = cls.env['round.instance'].create(
            {'template_id': cls.delivery_template.id, 'date': '2017-01-01'}
        )

        cls.warehouse_1 = cls.env['stock.warehouse'].create(
            {
                'name': 'Base Warehouse',
                'reception_steps': 'one_step',
                'delivery_steps': 'pick_ship',
                'code': 'BWH',
            }
        )
        cls.warehouse_1.pick_type_id.subcode = 'PICK'
        inventory = cls.env['stock.inventory'].create(
            {'name': 'Test', 'product_id': cls.p1.id, 'filter': 'product'}
        )
        inventory.prepare_inventory()
        assert not inventory.line_ids, "Inventory line should not created."
        cls.env['stock.inventory.line'].create(
            {
                'inventory_id': inventory.id,
                'product_id': cls.p1.id,
                'product_uom_id': cls.env.ref('product.product_uom_unit').id,
                'product_qty': 100,
                'location_id': cls.env.ref('stock.stock_location_stock').id,
            }
        )
        cls.env['stock.inventory.line'].create(
            {
                'inventory_id': inventory.id,
                'product_id': cls.p1.id,
                'product_uom_id': cls.env.ref('product.product_uom_unit').id,
                'product_qty': 100,
                'location_id': cls.warehouse_1.wh_output_stock_loc_id.id,
            }
        )
        inventory.action_done()

    @classmethod
    def _create_picking_pick(cls, partner=None):
        if not partner:
            partner = cls.partner1
        warehouse = cls.warehouse_1
        Picking = cls.env['stock.picking']
        picking_values = {
            'partner_id': partner.id,
            'picking_type_id': warehouse.pick_type_id.id,
            'location_id': cls.env.ref('stock.stock_location_stock').id,
            'location_dest_id': warehouse.wh_output_stock_loc_id.id,
            'move_lines': [
                (
                    0,
                    0,
                    {
                        'name': cls.p1.name,
                        'product_id': cls.p1.id,
                        'picking_type_id': warehouse.pick_type_id.id,
                        'product_uom_qty': 1,
                        'product_uom': cls.p1.uom_id.id,
                        'location_id': cls.env.ref(
                            'stock.stock_location_stock'
                        ).id,
                        'location_dest_id': warehouse.wh_output_stock_loc_id.id,
                    },
                )
            ],
        }
        return Picking.create(picking_values)

    @classmethod
    def _create_picking_out(cls, partner=None):
        if not partner:
            partner = cls.partner1
        warehouse = cls.warehouse_1
        Picking = cls.env['stock.picking']
        picking_values = {
            'partner_id': partner.id,
            'picking_type_id': warehouse.out_type_id.id,
            'location_id': warehouse.wh_output_stock_loc_id.id,
            'location_dest_id': cls.env.ref(
                'stock.stock_location_customers'
            ).id,
            'move_lines': [
                (
                    0,
                    0,
                    {
                        'name': cls.p1.name,
                        'product_id': cls.p1.id,
                        'picking_type_id': warehouse.out_type_id.id,
                        'product_uom_qty': 1,
                        'product_uom': cls.p1.uom_id.id,
                        'location_id': warehouse.wh_output_stock_loc_id.id,
                        'location_dest_id': cls.env.ref(
                            'stock.stock_location_customers'
                        ).id,
                    },
                )
            ],
        }
        return Picking.create(picking_values)

    @classmethod
    def _confirm_sale_order(
        cls, partner=None, product=None, qty=1, carrier_id=None
    ):
        if partner is None:
            partner = cls.partner1
        if product is None:
            product = cls.p1
        warehouse = cls.warehouse_1
        Sale = cls.env['sale.order']
        so_values = {
            'partner_id': partner.id,
            'warehouse_id': warehouse.id,
            'order_line': [
                (
                    0,
                    0,
                    {
                        'name': product.name,
                        'product_id': product.id,
                        'product_uom_qty': qty,
                        'product_uom': product.uom_id.id,
                        'price_unit': 1,
                    },
                )
            ],
        }
        if carrier_id:
            so_values["carrier_id"] = carrier_id
        so = Sale.create(so_values)
        so.action_confirm()
        return so
