# -*- coding: utf-8 -*-
# Copyright 2017 Julien Coux (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestDeliveryRoundOnDeliveryCarrier(TransactionCase):

    def setUp(self):
        super(TestDeliveryRoundOnDeliveryCarrier, self).setUp()

        self.partner = self.env['res.partner'].create({
            'name': 'Unittest partner',
        })

        self.p1 = self.env['product.template'].create({
            'name': 'Unittest P1',
            'uom_id': self.ref('product.product_uom_unit'),
            'type': 'consu',
        })

        self.deliver_carrier_fixed = self.env['delivery.carrier'].create({
            'name': 'Unittest shipping costs',
            'delivery_type': 'fixed',
            'fixed_price': 10.0,
        })

        self.delivery_vehicle = self.env['round.vehicle'].create({
            'name': 'Unittest delivery vehicle',
        })

        self.delivery_round_2 = self.env['round.instance'].create({
            'name': 'Unittest delivery round',
            'vehicle_id': self.delivery_vehicle.id,
            'date': '2017-02-01',
        })

        self.delivery_round_1 = self.env['round.instance'].create({
            'name': 'Unittest delivery round',
            'vehicle_id': self.delivery_vehicle.id,
            'date': '2017-01-01',
        })

    def test_01_without_delivery_round(self):
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
        self.assertFalse(sale.delivery_round_id)
        sale.action_confirm()
        self.assertFalse(sale.delivery_round_id)
        self.assertFalse(sale.picking_ids.delivery_round_id)

    def test_02_with_delivery_round(self):
        self.deliver_carrier_fixed.delivery_vehicle_id = (
            self.delivery_vehicle.id
        )
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
        self.assertFalse(sale.delivery_round_id)
        sale.action_confirm()
        self.assertEqual(sale.delivery_round_id, self.delivery_round_1)
        self.assertEqual(
            sale.picking_ids.delivery_round_id,
            self.delivery_round_1
        )
