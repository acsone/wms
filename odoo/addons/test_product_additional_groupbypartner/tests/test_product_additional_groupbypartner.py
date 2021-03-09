# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.product_additional.tests import common


class TestProductAdditionalGroupByPartner(common.StockPickingTestCase):
    @classmethod
    def setUpClass(cls):
        super(TestProductAdditionalGroupByPartner, cls).setUpClass()
        cls.warehouse_1.pick_type_id.groupbypartner = True
        cls.warehouse_1.out_type_id.groupbypartner = True
        cls.carrier_fixed = cls.env["delivery.carrier"].create(
            {
                "name": "Unittest shipping costs",
                "delivery_type": "fixed",
                "fixed_price": 10.0,
            }
        )

    def test_00(self):
        """
         Test case:
            PICk + SHIP configured to be grouped by partner
            1. Create and confirm a SO with product_additional for supplier1
               (1 main for 5 additionals)
            2. Create and confirm a new SO with product_additional for supplier1
               (1 main for 5 additionals)
        Expected result:
            1. 1 Move for additional product created for a total of 5
            2. 2 Moves for additional product created for a total of 10
        """
        sale = self._confirm_sale_order(
            products=[self.main_product], carrier_id=self.carrier_fixed.id
        )

        # check the pickings
        pick = sale.mapped("picking_ids").filtered(
            lambda p: p.picking_type_subcode == "PICK"
        )
        self.assertEqual(len(pick), 1)

        # Check that pick only has 1 move line before reservation
        self.assertEqual(len(pick.move_lines), 1)
        self.assertEqual(pick.move_lines.product_id.id, self.main_product.id)

        ship = sale.mapped("picking_ids").filtered(
            lambda p: p.picking_type_code == "outgoing"
        )
        self.assertEqual(len(ship), 1)

        pick.action_confirm()
        pick.action_assign()

        # Check that the additional product is taken into account after confirmation
        additional_move = pick.move_lines.filtered(
            lambda m, product=self.additional_product: m.product_id == product
        )
        self.assertEqual(additional_move.product_qty, 5)

        self.assertEqual(len(pick.move_lines), 2)
        self.assertEqual(len(pick.pack_operation_ids), 2)

        self.assertEqual(
            pick.mapped("pack_operation_ids.product_id"),
            self.main_product | self.additional_product,
        )

        # Check that the additional product is also added to the shipping after confirmation
        self.assertEqual(len(ship.move_lines), 2)

        new_sale = self._confirm_sale_order(
            products=[self.main_product], carrier_id=self.carrier_fixed.id
        )
        new_pick = new_sale.mapped("picking_ids").filtered(
            lambda p: p.picking_type_subcode == "PICK"
        )
        self.assertEqual(len(pick), 1)
        self.assertEqual(new_pick, pick)
        pick.action_assign()
        additional_moves = pick.move_lines.filtered(
            lambda m, product=self.additional_product: m.product_id == product
        )
        self.assertEqual(sum(additional_moves.mapped("product_qty")), 10)

        self.assertEqual(len(pick.move_lines), 4)  # 2 main + 2 additionnal
        self.assertEqual(len(pick.pack_operation_ids), 2)

    def test_01(self):
        """
        Test case:
            PICk + SHIP configured to be grouped by partner
            1. Create and confirm a SO with product with additional_product for
               supplier1 (1 main for 5 additionals)
            2. Create and confirm a new SO with product_additional as main
               product for supplier1 (2)
            3. Cancel the picking
        Expected result:
            1. 1 Move for additional product created for a total of 5
            2. 2 Moves for additional product created for a total of 7
            3. All pack ops are removed
        """
        # 1
        sale = self._confirm_sale_order(
            products=[self.main_product], carrier_id=self.carrier_fixed.id
        )
        pick = self._get_picking_pick(sale)
        self.assertEqual(len(pick), 1)

        # Check that pick only has 1 move line before reservation
        self.assertEqual(len(pick.move_lines), 1)
        self.assertEqual(pick.move_lines.product_id.id, self.main_product.id)

        pick.action_confirm()
        pick.action_assign()
        additional_move = pick.move_lines.filtered(
            lambda m, product=self.additional_product: m.product_id == product
        )
        self.assertEqual(additional_move.product_qty, 5)
        self.assertEqual(len(pick.pack_operation_ids), 2)
        additional_pack_op = self._get_pack_operations(pick, self.additional_product)
        self.assertEqual(additional_pack_op.product_qty, 5)
        # 2
        sale2 = self._confirm_sale_order(
            products=[self.additional_product], qty=2, carrier_id=self.carrier_fixed.id,
        )
        pick = self._get_picking_pick(sale2)
        pick.action_assign()
        additional_pack_op = self._get_pack_operations(pick, self.additional_product)
        self.assertEqual(1, len(additional_pack_op))
        self.assertEqual(additional_pack_op.product_qty, 7)
