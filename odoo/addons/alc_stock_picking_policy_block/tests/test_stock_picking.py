# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests.common import SavepointCase


class TestStockPicking(SavepointCase):
    @classmethod
    def setUpClass(cls):
        """
        Objets created:
            1 product
            2 stock locations (loc1, loc2)
            2 pickings with same subcode and procurement group and move_type = one
                pick1 from loc1 to customer with 1 line for product
                pick2 from loc2 to customer with 1 line for product
            product only available in loc 1
        pick1 1 is availavle
        pick2 is waiting availability
        """
        super(TestStockPicking, cls).setUpClass()
        cls.env = cls.env(
            context=dict(cls.env.context, tracking_disable=True, round_autoset=False)
        )

        cls.product = cls.env["product.product"].create(
            {
                "name": "Product sale_procurement",
                "type": "product",
                "uom_id": cls.env.ref("product.product_uom_unit").id,
                "uom_po_id": cls.env.ref("product.product_uom_unit").id,
                "default_code": "Code product sale_procurement",
                "barcode": "FFF00001",
            }
        )

        group = cls.env["procurement.group"].create({})

        wh = cls.env["stock.warehouse"].search([], limit=1)
        cls.location_1 = cls.env["stock.location"].create(
            {
                "name": "TestLocation1",
                "location_id": wh.view_location_id.id,
                "usage": "internal",
            }
        )
        cls.location_2 = cls.env["stock.location"].create(
            {
                "name": "TestLocation1",
                "location_id": wh.view_location_id.id,
                "usage": "internal",
            }
        )
        loc_customer = cls.env.ref("stock.stock_location_customers")

        pick_type = cls.env.ref("stock.picking_type_out")
        pick_type.subcode = "PICK"
        cls.picking_type = pick_type

        # Create test move 1
        cls.picking_1 = cls.env["stock.picking"].create(
            {
                "picking_type_id": pick_type.id,
                "location_id": cls.location_1.id,
                "location_dest_id": loc_customer.id,
                "move_type": "one",
            }
        )
        cls.move_1 = cls.env["stock.move"].create(
            {
                "picking_id": cls.picking_1.id,
                "name": "Test move 1",
                "product_id": cls.product.id,
                "product_uom": cls.product.uom_id.id,
                "product_uom_qty": 2,
                "location_id": cls.location_1.id,
                "location_dest_id": loc_customer.id,
                "date": "2018-01-01 00:00:00",
                "priority": "0",
                "group_id": group.id,
            }
        )
        cls.move_1.action_confirm()

        # Create test move 2
        cls.picking_2 = cls.env["stock.picking"].create(
            {
                "picking_type_id": pick_type.id,
                "location_id": cls.location_2.id,
                "location_dest_id": loc_customer.id,
                "move_type": "one",
            }
        )
        cls.move_2 = cls.env["stock.move"].create(
            {
                "picking_id": cls.picking_2.id,
                "name": "Test move 2",
                "product_id": cls.product.id,
                "product_uom": cls.product.uom_id.id,
                "product_uom_qty": 2,
                "location_id": cls.location_2.id,
                "location_dest_id": loc_customer.id,
                "date": "2018-01-02 00:00:00",
                "priority": "0",
                "group_id": group.id,
            }
        )
        cls.move_2.action_confirm()

        # put product stock in location 1
        cls._update_product_stock_qty(cls.product, 10, cls.location_1)
        cls.picking_1.action_assign()
        cls.picking_2.action_assign()

    @classmethod
    def _update_product_stock_qty(cls, product, qty, location):
        wiz = cls.env["stock.change.product.qty"].create(
            {
                "product_id": product.id,
                "product_tmpl_id": product.product_tmpl_id.id,
                "new_quantity": qty,
                "location_id": location.id,
            }
        )
        wiz.change_product_qty()

    def test_00(self):
        """
        Test data: (see setupClass)
            * picks with
                * move_type: one
                * same group_id
                * same subtype
            pick 1 assigned
            pick 2 confirmed
        Expected result
            is_blocked_by_picking_policy on both pickings must be True
        """
        for fn in ["move_type", "group_id", "picking_type_subcode"]:
            self.assertEqual(
                self.picking_1[fn], self.picking_2[fn], "%s should be equals" % fn
            )
        self.assertEqual(self.picking_1.state, "assigned")
        self.assertEqual(self.picking_2.state, "confirmed")
        self.assertTrue(self.picking_1.is_blocked_by_picking_policy)
        self.assertTrue(self.picking_2.is_blocked_by_picking_policy)

    def test_01(self):
        """
        Test data: (see setupClass)
            * picks with
                * move_type: one
                * same group_id
                * same subtype
            pick 1 assigned and is_blocked_by_picking_policy = True
            pick 2 confirmed and is_blocked_by_picking_policy = True
        Test case:
            remove the groupid on move 2
        Expected result
            pick 1 assigned and is_blocked_by_picking_policy = False -> no more part of the same group
            pick 2 confirmed and is_blocked_by_picking_policy = True
        """
        self.assertTrue(self.picking_1.is_blocked_by_picking_policy)
        self.assertTrue(self.picking_2.is_blocked_by_picking_policy)
        self.move_2.group_id = False
        self.assertFalse(self.picking_1.is_blocked_by_picking_policy)
        self.assertTrue(self.picking_2.is_blocked_by_picking_policy)

    def test_02(self):
        """
        Test data: (see setupClass)
            * picks with
                * move_type: one
                * same group_id
                * same subtype
            pick 1 assigned and is_blocked_by_picking_policy = True
            pick 2 confirmed and is_blocked_by_picking_policy = True
        Test case:
            update move_type to 'direct' on picking 1
        Expected result
             pick 1 assigned and is_blocked_by_picking_policy = False -> no more 'all at once'
            pick 2 confirmed and is_blocked_by_picking_policy = True
        """
        self.assertTrue(self.picking_1.is_blocked_by_picking_policy)
        self.assertTrue(self.picking_2.is_blocked_by_picking_policy)
        self.picking_1.move_type = "direct"
        self.assertFalse(self.picking_1.is_blocked_by_picking_policy)
        self.assertTrue(self.picking_2.is_blocked_by_picking_policy)

    def test_03(self):
        """
        Test data: (see setupClass)
            * picks with
                * move_type: one
                * same group_id
                * same subtype
            pick 1 assigned and is_blocked_by_picking_policy = True
            pick 2 confirmed and is_blocked_by_picking_policy = True
        Test case:
            update move_type to 'direct' on picking 2
        Expected result
             pick 1 assigned and is_blocked_by_picking_policy = False -> no more others 'all at once' picking not available
            pick 2 confirmed and is_blocked_by_picking_policy = False
        """
        self.assertTrue(self.picking_1.is_blocked_by_picking_policy)
        self.assertTrue(self.picking_2.is_blocked_by_picking_policy)
        self.picking_2.move_type = "direct"
        self.assertFalse(self.picking_1.is_blocked_by_picking_policy)
        self.assertFalse(self.picking_2.is_blocked_by_picking_policy)

    def test_04(self):
        """
        Test data: (see setupClass)
            * picks with
                * move_type: one
                * same group_id
                * same subtype
            pick 1 assigned and is_blocked_by_picking_policy = True
            pick 2 confirmed and is_blocked_by_picking_policy = True
        Test case:
            remove subtype
        Expected result
             pick 1 assigned and is_blocked_by_picking_policy = False -> The rule only apply if a subtype is specified and is the same...
             pick 2 confirmed and is_blocked_by_picking_policy = True
        """
        self.assertTrue(self.picking_1.is_blocked_by_picking_policy)
        self.assertTrue(self.picking_2.is_blocked_by_picking_policy)
        self.picking_type.subcode = False
        self.assertFalse(self.picking_1.is_blocked_by_picking_policy)
        self.assertTrue(self.picking_2.is_blocked_by_picking_policy)
