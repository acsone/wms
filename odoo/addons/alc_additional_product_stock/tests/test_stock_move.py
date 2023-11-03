# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import StockPickingTestCase


class TestStockMove(StockPickingTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
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

        ship = self._get_picking_ship(so)

        # Check that the additional product is also added to the shipping after confirmation
        self.assertEqual(len(ship.move_ids), 3)

        # Cancel stock move for main product
        main_product_move = ship.move_ids.filtered(
            lambda m: m.product_id.id == self.main_product.id
        )
        main_product_move._action_cancel()

        self.assertEqual(main_product_move.state, "cancel")
        additional_move = self._get_additional_move(ship)
        self.assertFalse(additional_move)

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
        ship = self._get_picking_ship(so2)
        # Check that the additional product is also added to the shipping after confirmation
        self.assertEqual(len(ship.move_ids), 4)

        # Cancel stock move for main product
        main_product_move = ship.move_ids.filtered(
            lambda m: m.product_id.id == self.main_product.id
        )
        main_product_move._action_cancel()

        self.assertEqual(main_product_move.state, "cancel")
        additional_product_move = main_product_move.additional_move_ids
        self.assertEqual(additional_product_move.state, "cancel")

        second_main_product = ship.move_ids.filtered(
            lambda m: m.product_id.id == self.main_product2.id
        )
        second_additional_product_move = second_main_product.additional_move_ids
        self.assertEqual(second_additional_product_move.state, "waiting")
