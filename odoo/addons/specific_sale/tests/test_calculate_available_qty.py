# -*- coding: utf-8 -*-
# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from datetime import datetime, timedelta

from odoo import fields
from odoo.tests.common import SavepointCase


class TestCalcAvailableQty(SavepointCase):

    at_install = False
    post_install = True

    @classmethod
    def setUpClass(cls):
        super(TestCalcAvailableQty, cls).setUpClass()
        cls.location_model = cls.env['stock.location']
        cls.inventory_model = cls.env['stock.inventory']
        cls.inventory_line_model = cls.env['stock.inventory.line']
        cls.stock_location_model = cls.env['stock.location']
        cls.stock_location = cls.env.ref('stock.stock_location_stock')
        # cls.supplier_location = cls.env.ref('stock.stock_location_suppliers')
        cls.tax = cls.env["account.tax"].create(
            {
                'name': 'Unittest tax',
                'price_include': False,
                'amount_type': 'percent',
                'amount': '0',
            }
        )

        cls.p1 = cls.env['product.template'].create(
            {
                'name': 'Unittest P1',
                'uom_id': cls.env.ref('product.product_uom_unit').id,
                'type': 'product',
            }
        )

        cls.partner = cls.env['res.partner'].create(
            {'name': 'Unittest partner', 'ref': '4929752'}
        )

        cls.location_parking = cls.stock_location_model.create(
            {
                'name': 'Product parking',
                'kind': 'bin',
                'zone': 'A',
                'corridor': 'P',
                'shelf': 'A',
                'height': '1',
                'box': '1',
                'location_id': cls.stock_location.location_id.id,
                'exclude_from_immediately_usable_qty': True,
            }
        )
        cls.location_parking._parent_store_compute()
        cls.customer_location = cls.env.ref('stock.stock_location_customers')
        cls.loss_loc = cls.env.ref('stock_lot_loss.stock_location_14019')
        cls.loss_loc.location_id = cls.stock_location.location_id
        cls.loss_loc._parent_store_compute()
        cls._define_product_qty(cls.stock_location, cls.p1, 10.0)

    @classmethod
    def _define_product_qty(cls, location, product, quantity):
        inventory = cls.inventory_model.create(
            {
                'name': 'Unittest Inventory',
                'location_id': location.id,
                'filter': 'partial',
            }
        )
        inventory.prepare_inventory()
        cls.inventory_line_model.create(
            {
                'inventory_id': inventory.id,
                'product_id': product.product_variant_ids.id,
                'location_id': location.id,
                'product_qty': quantity,
            }
        )
        inventory.action_done()

    def _create_move(
        self,
        stock_location,
        customer_location,
        date,
        confirm=True,
        transfer=False,
    ):
        picking_out = self.env['stock.picking'].create(
            {
                'partner_id': self.env.ref('base.res_partner_2').id,
                'picking_type_id': self.env.ref('stock.picking_type_out').id,
                'location_id': stock_location.id,
                'location_dest_id': customer_location.id,
            }
        )
        self.env['stock.move'].create(
            {
                'name': self.p1.name,
                'product_id': self.p1.product_variant_ids.id,
                'product_uom_qty': 5,
                'product_uom': self.p1.uom_id.id,
                'picking_id': picking_out.id,
                'location_id': stock_location.id,
                'location_dest_id': customer_location.id,
                'date': fields.Datetime.to_string(date),
            }
        )
        if confirm or transfer:
            picking_out.action_confirm()
        if transfer:
            picking_out.force_assign()
            picking_out.do_transfer()

    def test_inventory(self):
        self._define_product_qty(self.stock_location, self.p1, 10.0)
        self.p1.refresh()
        self.assertEqual(self.p1.immediately_usable_qty, 10.0)

    def test_parking_excluded(self):
        self.p1 = self.p1.with_context(
            prio=1, date=fields.Datetime.to_string(datetime.now())
        )
        self.assertEqual(self.p1.immediately_usable_qty, 10.0)
        self._define_product_qty(self.location_parking, self.p1, 30.0)
        self.p1.refresh()
        self.assertEqual(self.p1.virtual_available, 40.0)
        self.assertEqual(self.p1.immediately_usable_qty, 10.0)

    def test_same_prio(self):
        self.p1 = self.p1.with_context(
            prio=1,
            date=fields.Datetime.to_string(datetime.now() + timedelta(days=1)),
        )

        self._create_move(
            self.stock_location, self.customer_location, datetime.now()
        )
        self.p1.refresh()
        self.assertEqual(self.p1.immediately_usable_qty, 5.0)

    def test_higher_prio(self):
        self.p1 = self.p1.with_context(
            prio=2,
            date=fields.Datetime.to_string(datetime.now() + timedelta(days=1)),
        )
        self._create_move(
            self.stock_location, self.customer_location, datetime.now()
        )
        self.p1.refresh()
        self.assertEqual(self.p1.immediately_usable_qty, 10.0)

    def test_same_prio_later_date(self):
        self.p1 = self.p1.with_context(
            prio=1, date=fields.Datetime.to_string(datetime.now())
        )

        self._create_move(
            self.stock_location,
            self.customer_location,
            datetime.now() + timedelta(days=1),
        )
        self.p1.refresh()
        self.assertEqual(self.p1.immediately_usable_qty, 10.0)

    def test_deduct_loss_inc_default(self):
        self.p1 = self.p1.with_context(
            prio=1,
            date=fields.Datetime.to_string(datetime.now() + timedelta(days=1)),
        )
        self._create_move(self.stock_location, self.loss_loc, datetime.now())
        self.p1.refresh()
        self.assertEqual(self.p1.immediately_usable_qty, 5.0)

    def test_deduct_loss_existing(self):
        self.p1 = self.p1.with_context(
            prio=1, date=fields.Datetime.to_string(datetime.now())
        )
        self._create_move(
            self.stock_location, self.loss_loc, datetime.now(), transfer=True
        )
        self.p1.refresh()
        self.assertEqual(self.p1.immediately_usable_qty, 5.0)

    def test_deduct_loss_inc_high_prio(self):
        self.p1 = self.p1.with_context(
            prio=2,
            date=fields.Datetime.to_string(datetime.now() + timedelta(days=1)),
        )
        self._create_move(self.stock_location, self.loss_loc, datetime.now())
        self.p1.refresh()
        self.assertEqual(self.p1.immediately_usable_qty, 5.0)

    def test_deduct_loss_inc_later_date(self):
        self.p1 = self.p1.with_context(
            prio=1, date=fields.Datetime.to_string(datetime.now())
        )
        self._create_move(
            self.stock_location,
            self.loss_loc,
            datetime.now() + timedelta(days=1),
        )
        self.p1.refresh()
        self.assertEqual(self.p1.immediately_usable_qty, 5.0)
