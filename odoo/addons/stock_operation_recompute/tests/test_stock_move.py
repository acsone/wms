# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.product_additional.tests import common


class TestStockMove(common.StockPickingTestCase):
    def test_00(self):
        """
        Data:
            Create, confirm assign one SO with 1 product additional
        Test case:
            Recompute pack_op on the main product
        Expected:
            Only one stock move should exists for the additional product with
            the associated pack op
        """
        # Create the sale order without setting a sequence on sale order lines
        so = self._confirm_sale_order(products=[self.main_product])
        # check the pickings
        pick = so.mapped("picking_ids").filtered(
            lambda p: p.picking_type_subcode == "PICK"
        )

        ship = so.mapped("picking_ids").filtered(
            lambda p: p.picking_type_code == "outgoing"
        )

        pick.action_confirm()
        pick.action_assign()

        pick_main_product_id = pick.move_lines.filtered(
            lambda a, product=self.main_product: a.product_id == product
        )

        pick_addition_product_move = pick.move_lines.filtered(
            lambda a, additional_product=self.additional_product: a.product_id
            == additional_product
        )
        ship_addition_product_move = ship.move_lines.filtered(
            lambda a, additional_product=self.additional_product: a.product_id
            == additional_product
        )
        self.assertTrue(pick_addition_product_move)
        self.assertEqual(
            pick_addition_product_move.linked_move_operation_ids.operation_id.product_qty,
            5,
        )
        self.assertTrue(ship_addition_product_move)

        # recompute pack op
        pick_main_product_id._recompute_pack_op()

        new_pick_addition_product_move = pick.move_lines.filtered(
            lambda a, additional_product=self.additional_product: a.product_id
            == additional_product
        )
        new_ship_addition_product_move = ship.move_lines.filtered(
            lambda a, additional_product=self.additional_product: a.product_id
            == additional_product
        )
        self.assertTrue(new_pick_addition_product_move)
        self.assertEqual(
            new_pick_addition_product_move.linked_move_operation_ids.operation_id.product_qty,
            5,
        )
        self.assertTrue(new_ship_addition_product_move)

    def test_01(self):
        """
        Data:
            Create, confirm assign one SO with 1 product additional
        Test case:
            Recompute pack_op on the additional product
        Expected:
            Only one stock move should exists for the additional product with
            the associated pack op
        """
        # Create the sale order without setting a sequence on sale order lines
        so = self._confirm_sale_order(products=[self.main_product])
        # check the pickings
        pick = so.mapped("picking_ids").filtered(
            lambda p: p.picking_type_subcode == "PICK"
        )

        ship = so.mapped("picking_ids").filtered(
            lambda p: p.picking_type_code == "outgoing"
        )

        pick.action_confirm()
        pick.action_assign()

        pick_addition_product_move = pick.move_lines.filtered(
            lambda a, additional_product=self.additional_product: a.product_id
            == additional_product
        )
        ship_addition_product_move = ship.move_lines.filtered(
            lambda a, additional_product=self.additional_product: a.product_id
            == additional_product
        )
        self.assertTrue(pick_addition_product_move)
        self.assertEqual(
            pick_addition_product_move.linked_move_operation_ids.operation_id.product_qty,
            5,
        )
        self.assertTrue(ship_addition_product_move)

        # recompute pack op
        pick_addition_product_move._recompute_pack_op()

        new_pick_addition_product_move = pick.move_lines.filtered(
            lambda a, additional_product=self.additional_product: a.product_id
            == additional_product
        )
        new_ship_addition_product_move = ship.move_lines.filtered(
            lambda a, additional_product=self.additional_product: a.product_id
            == additional_product
        )
        self.assertTrue(new_pick_addition_product_move)
        self.assertEqual(
            new_pick_addition_product_move.linked_move_operation_ids.operation_id.product_qty,
            5,
        )
        self.assertTrue(new_ship_addition_product_move)

    def test_02(self):
        """
        Data:
            Create, confirm assign one SO with 1 product additional
            Set qty done on pack operation for the additional move
        Test case:
            Recompute pack_op on the main product
        Expected:
            Only one stock move should exists for the additional product with
            1 associated pack op with qty_done = 3
        """
        # Create the sale order without setting a sequence on sale order lines
        so = self._confirm_sale_order(products=[self.main_product])
        # check the pickings
        pick = so.mapped("picking_ids").filtered(
            lambda p: p.picking_type_subcode == "PICK"
        )

        ship = so.mapped("picking_ids").filtered(
            lambda p: p.picking_type_code == "outgoing"
        )

        pick.action_confirm()
        pick.action_assign()

        pick_main_product_id = pick.move_lines.filtered(
            lambda a, product=self.main_product: a.product_id == product
        )

        pick_addition_product_move = pick.move_lines.filtered(
            lambda a, additional_product=self.additional_product: a.product_id
            == additional_product
        )
        pick_addition_product_move.linked_move_operation_ids.operation_id.qty_done = 3

        # recompute pack op
        pick_main_product_id._recompute_pack_op()

        new_pick_addition_product_move = pick.move_lines.filtered(
            lambda a, additional_product=self.additional_product: a.product_id
            == additional_product
        )
        new_ship_addition_product_move = ship.move_lines.filtered(
            lambda a, additional_product=self.additional_product: a.product_id
            == additional_product
        )
        self.assertTrue(new_pick_addition_product_move)
        self.assertEqual(
            new_pick_addition_product_move.linked_move_operation_ids.operation_id.product_qty,
            5,
        )
        self.assertEqual(
            new_pick_addition_product_move.linked_move_operation_ids.operation_id.qty_done,
            3,
        )
        self.assertTrue(new_ship_addition_product_move)

    def test_03(self):
        """
        Data:
            Create, confirm assign one SO with 1 product additional
            Set qty done on pack operation for the additional move
        Test case:
            Recompute pack_op on the additional product
        Expected:
            Only one stock move should exists for the additional product with
            1 associated pack op with qty_done = 3
        """
        # Create the sale order without setting a sequence on sale order lines
        so = self._confirm_sale_order(products=[self.main_product])
        # check the pickings
        pick = so.mapped("picking_ids").filtered(
            lambda p: p.picking_type_subcode == "PICK"
        )

        ship = so.mapped("picking_ids").filtered(
            lambda p: p.picking_type_code == "outgoing"
        )

        pick.action_confirm()
        pick.action_assign()

        pick_addition_product_move = pick.move_lines.filtered(
            lambda a, additional_product=self.additional_product: a.product_id
            == additional_product
        )
        pick_addition_product_move.linked_move_operation_ids.operation_id.qty_done = 3

        # recompute pack op
        pick_addition_product_move._recompute_pack_op()

        new_pick_addition_product_move = pick.move_lines.filtered(
            lambda a, additional_product=self.additional_product: a.product_id
            == additional_product
        )
        new_ship_addition_product_move = ship.move_lines.filtered(
            lambda a, additional_product=self.additional_product: a.product_id
            == additional_product
        )
        self.assertTrue(new_pick_addition_product_move)
        self.assertEqual(
            new_pick_addition_product_move.linked_move_operation_ids.operation_id.product_qty,
            5,
        )
        self.assertEqual(
            new_pick_addition_product_move.linked_move_operation_ids.operation_id.qty_done,
            3,
        )
        self.assertTrue(new_ship_addition_product_move)
