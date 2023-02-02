# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import StockPickingTestCase


class TestStockPicking(StockPickingTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, round_autoset=False))

    def test_pick_and_ship(self):
        sale = self._confirm_sale_order(products=[self.main_product])

        # check the pickings
        pick = self._get_picking_pick(sale)
        self.assertEqual(len(pick), 1)

        ship = self._get_picking_ship(sale)
        self.assertEqual(len(ship), 1)

        pick.action_confirm()
        pick._action_done()

        # Check that the additional product is taken into account after confirmation
        self.assertEqual(len(pick.move_ids), 2)
        # Check that the additional product is also added to the shipping after confirmation
        self.assertEqual(len(ship.move_ids), 2)

        # The move created for the additional product into the pick picking
        # must be linked to the move for the additional product into the ship
        pick_addition_product_move = pick.move_ids.filtered(
            lambda a, additional_product=self.additional_product: a.product_id
            == additional_product
        )
        ship_addition_product_move = ship.move_ids.filtered(
            lambda a, additional_product=self.additional_product: a.product_id
            == additional_product
        )
        self.assertEqual(
            pick_addition_product_move.move_dest_ids, ship_addition_product_move
        )

    def test_00(self):
        """
        Test case:

            Create and confirm a SO with product_additional
            Confirm the picking (required to get the additional product into the picking)
            Cancel the SO
        Expected result:
            SO and pickings must be canceled
        """
        sale = self._confirm_sale_order(products=[self.main_product])
        pick = self._get_picking_pick(sale)
        # Add the move for the additional product into the picking...
        pick.action_confirm()
        pick.action_assign()
        # Check that the additional product is taken into account after confirmation
        self.assertEqual(len(pick.move_ids), 2)

        # At this stage the sale order is confirmed
        self.assertEqual(sale.state, "sale")

        # cancel it
        sale.with_context(disable_cancel_warning=True).action_cancel()

        # everything must be canceled
        self.assertEqual(sale.state, "cancel")
        self.assertEqual(len(pick), 1)
        self.assertEqual(pick.state, "cancel")
        ship = self._get_picking_ship(sale)
        self.assertEqual(len(ship), 1)
        self.assertEqual(ship.state, "cancel")

    def test_01(self):
        """
        Test case:

            Create and confirm a SO with product_additional
            Confirm the picking (required to get the additional product into the picking) and process
            Confirm and process the delivery
        Expected result:
            The qty_delivered on the so line must be the ordered qty
        """
        sale = self._confirm_sale_order(products=[self.main_product])
        pick = self._get_picking_pick(sale)
        # Add the move for the additional product into the picking and process
        # the picking...
        pick.action_confirm()
        pick.action_assign()
        for move in pick.move_ids:
            move.quantity_done = move.product_qty
        pick._action_done()
        ship = self._get_picking_ship(sale)
        ship.action_confirm()
        ship.action_assign()
        for move in ship.move_ids:
            move.quantity_done = move.product_qty
        ship._action_done()

        self.assertEqual(sale.order_line[0].qty_delivered, 1)

    def test_02(self):
        """
        Test case:

            Create and confirm a SO with product_additional
            Confirm the picking (required to get the additional product into the picking)
        Expected result:
            The moves for the additional product are linked to a warehouse...
        """
        sale = self._confirm_sale_order(products=[self.main_product])
        pick = self._get_picking_pick(sale)
        # Add the move for the additional product into the picking...
        pick.action_confirm()
        pick.action_assign()
        # Check that the additional product is taken into account after confirmation
        additional_move = pick.move_ids.filtered(
            lambda m, product=self.additional_product: m.product_id == product
        )
        self.assertEqual(additional_move.warehouse_id, self.warehouse_1)
        ship = self._get_picking_ship(sale)
        additional_move = ship.move_ids.filtered(
            lambda m, product=self.additional_product: m.product_id == product
        )
        self.assertEqual(additional_move.warehouse_id, self.warehouse_1)

    def test_03(self):
        """
        Test case:

            Create and confirm a SO with product_additional ( 1 main for 5 additional)
            1. Confirm the picking (required to get the additional product into the picking)
            2. unreserve
            3. Confirm the picking again
        Expected result:
            1. Move for additional product created
            2.
            3. No new move for additional product created
        """
        sale = self._confirm_sale_order(products=[self.main_product])
        pick = self._get_picking_pick(sale)
        # Add the move for the additional product into the picking...
        pick.action_confirm()
        pick.action_assign()
        # 1
        additional_move = pick.move_ids.filtered(
            lambda m, product=self.additional_product: m.product_id == product
        )
        self.assertEqual(additional_move.product_qty, 5)
        ship = self._get_picking_ship(sale)
        additional_move = ship.move_ids.filtered(
            lambda m, product=self.additional_product: m.product_id == product
        )
        self.assertEqual(len(additional_move), 1)
        self.assertEqual(additional_move.product_qty, 5)
        # 2
        pick.do_unreserve()
        pick.action_assign()
        # 3
        additional_move = pick.move_ids.filtered(
            lambda m, product=self.additional_product: m.product_id == product
        )
        self.assertEqual(len(additional_move), 1)
        self.assertEqual(additional_move.product_qty, 5)
        ship = self._get_picking_ship(sale)
        additional_move = ship.move_ids.filtered(
            lambda m, product=self.additional_product: m.product_id == product
        )
        self.assertEqual(additional_move.product_qty, 5)

    def test_04(self):
        """
        Test case:

            Create and confirm a SO with product_additional ( 1 main for 5 additional)
            1. Confirm and assign the picking (required to get the additional product into the picking)
            2. Confirm and assign the picking again
        Expected result:
            1. Move for additional product created
            2. No new move for additional product created
        """
        sale = self._confirm_sale_order(products=[self.main_product])
        pick = self._get_picking_pick(sale)
        # Add the move for the additional product into the picking...
        pick.action_confirm()
        pick.action_assign()
        # 1
        additional_move = pick.move_ids.filtered(
            lambda m, product=self.additional_product: m.product_id == product
        )
        self.assertEqual(additional_move.product_qty, 5)
        ship = self._get_picking_ship(sale)
        additional_move = ship.move_ids.filtered(
            lambda m, product=self.additional_product: m.product_id == product
        )
        self.assertEqual(len(additional_move), 1)
        self.assertEqual(additional_move.product_qty, 5)
        # 2
        pick.action_assign()
        additional_move = pick.move_ids.filtered(
            lambda m, product=self.additional_product: m.product_id == product
        )
        self.assertEqual(len(additional_move), 1)
        self.assertEqual(additional_move.product_qty, 5)
        ship = self._get_picking_ship(sale)
        additional_move = ship.move_ids.filtered(
            lambda m, product=self.additional_product: m.product_id == product
        )
        self.assertEqual(additional_move.product_qty, 5)

    def test_05(self):
        """
        Test case:

            Create and confirm a SO with 2 product_additional
                (1 main for 5 additional)
                (1 main for 3 additional)
            main_product -> 1 / 5 additional
            main_product_bis -> 1 / 3 additional
            Confirm and assign the picking (required to get the additional product into the picking)
        Expected result:
            *. Moves for additional product created (one by main product_id)
            *. 1 packop created for additional product (qty = 8)
        """
        self.main_product.ratio_additional_product = 5
        self.main_product2.ratio_additional_product = 3
        sale = self._confirm_sale_order(
            products=[self.main_product, self.main_product2]
        )
        pick = self._get_picking_pick(sale)
        # Add the move for the additional product into the picking...
        pick.action_confirm()
        pick.action_assign()

        additional_moves = pick.move_ids.filtered(
            lambda m, product=self.additional_product: m.product_id == product
        )
        self.assertEqual(len(additional_moves), 1)
        self.assertEqual(sum(additional_moves.mapped("product_qty")), 8)

        ship = self._get_picking_ship(sale)
        additional_moves = ship.move_ids.filtered(
            lambda m, product=self.additional_product: m.product_id == product
        )
        self.assertEqual(len(additional_moves), 2)
        self.assertEqual(sum(additional_moves.mapped("product_qty")), 8)

    def test_06(self):
        """
        Test case:

            1. Create validate and assign a SO with:
               * 1 main product (-> 5 additional)
               * 1 additional_product
            2. unreserve the picking
        Expected result:
            1.
              3 moves must be created:
                * one for main product
                * one for 5 additional product with is_additionnal and a link to maine move
                * one for 2 additional product without is_additionnal
              2 pack operations must exists:
                * one for main product (qty 1)
                * one for product_additional (qty 6)
            2. After unreserve, all the pack operation must be removed
        """
        self.main_product.ratio_additional_product = 5
        sale = self._confirm_sale_order(
            products=[self.main_product, self.additional_product]
        )
        pick = self._get_picking_pick(sale)
        # Add the move for the additional product into the picking...
        pick.action_confirm()
        pick.action_assign()
        additional_moves = pick.move_ids.filtered(
            lambda m, product=self.additional_product: m.product_id == product
        )
        self.assertEqual(sum(additional_moves.mapped("product_qty")), 6)
