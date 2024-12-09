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

    def test_pick_and_main_becomes_unavailable(self):
        """
        Test case:

                Create and confirm a SO with product_additional for the 2 main products
                main_product and main_product2
                Confirm the picking (required to get the additional product into the picking)
                Pick the additional product
                Unreserve main_product and make it unavailable
                Confirm the picking

        Expected result:
            The additional product move must not be canceled into the pick and the ship
        """
        sale = self._confirm_sale_order(
            products=[self.main_product, self.main_product2]
        )

        # check the pickings
        pick = self._get_picking_pick(sale)
        self.assertEqual(len(pick), 1)

        ship = self._get_picking_ship(sale)
        self.assertEqual(len(ship), 1)

        pick.action_confirm()

        # Pick the additional product
        pick_move = pick.move_ids.filtered(
            lambda m, product=self.additional_product: m.product_id == product
        )
        pick_move.quantity_done = pick_move.product_qty

        # Pick the main_product2
        pick_move = pick.move_ids.filtered(
            lambda m, product=self.main_product2: m.product_id == product
        )
        pick_move.quantity_done = pick_move.product_qty

        # Unreserve the main product and make it unavailable
        self.env["stock.quant"].with_context(inventory_mode=True).create(
            {
                "product_id": self.main_product.id,
                "inventory_quantity": 0.0,
                "location_id": self.loc_stock.id,
            }
        )._apply_inventory()

        # confirm the picking
        pick._action_done()

        # Check that the additional product is available into the ship
        self.assertEqual(len(ship.move_ids), 4)
        shop_addition_product_move = ship.move_ids.filtered(
            lambda a, additional_product=self.additional_product: a.product_id
            == additional_product
        )
        self.assertListEqual(
            shop_addition_product_move.mapped("state"), ["assigned", "assigned"]
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

        # Check that the additional product is taken into account after confirmation
        self.assertEqual(len(pick.move_ids), 2)
        # At this stage the sale order is confirmed
        self.assertIn(sale.state, ("sale", "done"))

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
        # Check that the additional product is taken into account after confirmation
        additional_move = self._get_additional_move(self._get_picking_pick(sale))
        self.assertEqual(additional_move.warehouse_id, self.warehouse_1)
        additional_move = self._get_additional_move(self._get_picking_ship(sale))
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
        # 1
        additional_move = self._get_additional_move(pick)
        self._check_move_assigned(additional_move, 5)
        ship = self._get_picking_ship(sale)
        additional_move = self._get_additional_move(ship)
        self.assertEqual(len(additional_move), 1)
        self.assertEqual(additional_move.product_qty, 5)
        # 2
        pick.do_unreserve()
        pick.action_assign()
        # 3
        additional_move = self._get_additional_move(pick)
        self.assertEqual(len(additional_move), 1)
        self._check_move_assigned(additional_move, 5)
        ship = self._get_picking_ship(sale)
        additional_move = self._get_additional_move(ship)
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

        # 1
        additional_move = self._get_additional_move(pick)
        self._check_move_assigned(additional_move, 5)
        ship = self._get_picking_ship(sale)
        additional_move = self._get_additional_move(ship)
        self.assertEqual(len(additional_move), 1)
        self.assertEqual(additional_move.product_qty, 5)
        # 2
        pick.action_assign()
        additional_move = self._get_additional_move(pick)
        self.assertEqual(len(additional_move), 1)
        self._check_move_assigned(additional_move, 5)
        ship = self._get_picking_ship(sale)
        additional_move = self._get_additional_move(ship)
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
        additional_move = self._get_additional_move(self._get_picking_pick(sale))
        self.assertEqual(len(additional_move), 1)
        self._check_move_assigned(additional_move, 8)
        additional_moves = self._get_additional_move(self._get_picking_ship(sale))
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

        additional_move = self._get_additional_move(pick)
        self._check_move_assigned(additional_move, 5)
        other_additional_move = pick.move_ids.filtered(
            lambda m, product=self.additional_product: m.product_id == product
            and not m.is_additional_move
        )
        self._check_move_assigned(other_additional_move, 1)

    def test_07(self):
        """Check that not done quantity of additional moves are canceled."""
        self.env["stock.quant"]._update_available_quantity(
            self.additional_product, self.loc_stock, -498
        )
        sale = self._confirm_sale_order(products=[self.main_product])
        pick = self._get_picking_pick(sale)
        pick.move_ids.move_line_ids.write({"qty_done": 1})
        additional_move = self._get_additional_move(pick)
        self.assertEqual(additional_move.product_uom_qty, 5)
        pick._action_done()
        self.assertEqual(pick.state, "done")
        self.assertEqual(additional_move.product_uom_qty, 1)
        self.assertEqual(additional_move.quantity_done, 1)
        backorder = self.env["stock.picking"].search([("backorder_id", "=", pick.id)])
        backorder_additional_move = backorder.move_ids
        self.assertTrue(backorder_additional_move.is_additional_move)
        self.assertEqual(backorder_additional_move.product_uom_qty, 4)
        self.assertEqual(backorder_additional_move.state, "partially_available")

        ship = self._get_picking_ship(sale)
        ship.picking_type_id.no_backorder_for_additional_product = True
        ship.action_assign()
        self.assertEqual(ship.state, "assigned")
        additional_move = self._get_additional_move(ship)
        self.assertEqual(additional_move.product_uom_qty, 5)
        ship.move_ids.move_line_ids.write({"qty_done": 1})
        ship._action_done()
        self.assertEqual(ship.state, "done")
        backorder = self.env["stock.picking"].search([("backorder_id", "=", ship.id)])
        self.assertFalse(backorder)
        self.assertEqual(len(ship.move_ids), 3)
        self.assertEqual(ship.move_ids[2].state, "cancel")
        self.assertEqual(backorder_additional_move.state, "cancel")

    def test_partial_cancel_with_package(self):
        """
        A sale order with:

            - 3 main products

        A partial picking transfer of the main product
        A complete picking transfer of the additional product

        Those operations have been put in pack
        """
        sale = self._confirm_sale_order(products=[self.main_product], qty=3.0)

        pick = self._get_picking_pick(sale)

        # Transfer partial quantity with backorder
        main = pick.move_line_ids.filtered(
            lambda line: line.product_id == self.main_product
        )
        main.qty_done = 2.0
        additional = pick.move_line_ids - main
        additional.qty_done = 15.0
        pick._put_in_pack(pick.move_line_ids)

        pick._action_done()

        # Try to validate the delivery picking
        ship = self._get_picking_ship(sale)
        ship.picking_type_id.no_backorder_for_additional_product = True
        ship.package_level_ids.is_done = True
        ship._action_done()
