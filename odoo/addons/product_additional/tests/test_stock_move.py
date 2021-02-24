# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

# from odoo.tests import common

from . import common


class TestStockMove(common.StockPickingTestCase):
    @classmethod
    def setUpClass(cls):
        super(TestStockMove, cls).setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, round_autoset=False))

    def test_00(self):
        """
        Data:
        one SO is created with one picking and stock moves associated
        Test case:
        we cancel one move for the main product, the move for the additionnal one should also be cancelled
        Expected:
        move for the additionnal product is cancelled

        """
        # Create the sale order without setting a sequence on sale order lines
        so = self._confirm_sale_order(products=[self.main_product, self.product_2])
        # check the pickings
        pick = so.mapped("picking_ids").filtered(
            lambda p: p.picking_type_subcode == "PICK"
        )

        ship = so.mapped("picking_ids").filtered(
            lambda p: p.picking_type_code == "outgoing"
        )

        pick.action_confirm()
        pick.action_assign()

        # Check that the additional product is also added to the shipping after confirmation
        self.assertEqual(len(ship.move_lines), 3)

        # Cancel stock move for main product
        main_product_move = ship.move_lines.filtered(
            lambda m: m.product_id.id == self.main_product.id
        )
        main_product_move.action_cancel()

        self.assertEqual(main_product_move.state, "cancel")
        additionnal_product_move = ship.move_lines.filtered(
            lambda a, additional_product=self.additional_product: a.product_id
            == additional_product
        )
        self.assertEqual(additionnal_product_move.state, "cancel")

    def test_01(self):
        """
        Data:
        one SO is created with one picking and stock moves associated.
        We have 2 products with the same additional product
        Test case:
        we cancel one move for one main product, the move for the additionnal one should also be cancelled
        but not the additional move for the other product
        Expected:
        one additional move is cancelled

        """

        # Create the sale order without setting a sequence on sale order lines
        so2 = self._confirm_sale_order(products=[self.main_product, self.main_product2])

        # check the pickings
        pick = so2.mapped("picking_ids").filtered(
            lambda p: p.picking_type_subcode == "PICK"
        )

        ship = so2.mapped("picking_ids").filtered(
            lambda p: p.picking_type_code == "outgoing"
        )

        pick.action_confirm()
        pick.action_assign()

        # Check that the additional product is also added to the shipping after confirmation
        self.assertEqual(len(ship.move_lines), 4)

        # Cancel stock move for main product
        main_product_move = ship.move_lines.filtered(
            lambda m: m.product_id.id == self.main_product.id
        )
        main_product_move.action_cancel()

        self.assertEqual(main_product_move.state, "cancel")
        additional_product_move = ship.move_lines.filtered(
            lambda a: a.is_additional_move
            and a.procurement_id == main_product_move.procurement_id
        )
        self.assertEqual(additional_product_move.state, "cancel")

        second_main_product = ship.move_lines.filtered(
            lambda m: m.product_id.id == self.main_product2.id
        )
        second_additional_product_move = ship.move_lines.filtered(
            lambda a: a.is_additional_move
            and a.procurement_id == second_main_product.procurement_id
        )
        self.assertEqual(second_additional_product_move.state, "waiting")
