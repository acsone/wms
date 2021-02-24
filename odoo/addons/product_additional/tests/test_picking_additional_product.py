# -*- coding: utf-8 -*-


from . import common


class TestStockPicking(common.StockPickingTestCase):
    @classmethod
    def setUpClass(cls):
        super(TestStockPicking, cls).setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, round_autoset=False))

    def test_pick_and_ship(self):
        sale = self._confirm_sale_order(products=[self.main_product])

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
        self.assertEqual(len(pick.move_lines), 2)
        self.assertEqual(len(pick.pack_operation_ids), 2)

        self.assertEqual(
            pick.mapped("pack_operation_ids.product_id"),
            self.main_product | self.additional_product,
        )

        # Check that the additional product is also added to the shipping after confirmation
        self.assertEqual(len(ship.move_lines), 2)

        # The move created for the additional product into the pick picking
        # must be linked to the move for the additional product into the ship
        pick_addition_product_move = pick.move_lines.filtered(
            lambda a, additional_product=self.additional_product: a.product_id
            == additional_product
        )
        ship_addition_product_move = ship.move_lines.filtered(
            lambda a, additional_product=self.additional_product: a.product_id
            == additional_product
        )
        self.assertEqual(
            pick_addition_product_move.move_dest_id, ship_addition_product_move
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
        pick = sale.mapped("picking_ids").filtered(
            lambda p: p.picking_type_subcode == "PICK"
        )
        # Add the move for the additional product into the picking...
        pick.action_confirm()
        pick.action_assign()
        # Check that the additional product is taken into account after confirmation
        self.assertEqual(len(pick.move_lines), 2)

        # At this stage the sale order is confirmed
        self.assertEqual(sale.state, "sale")

        # cancel it
        sale.action_cancel()

        # everything must be canceled
        self.assertEqual(sale.state, "cancel")
        self.assertEqual(len(pick), 1)
        self.assertEqual(pick.state, "cancel")
        ship = sale.mapped("picking_ids").filtered(
            lambda p: p.picking_type_code == "outgoing"
        )
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
        pick = sale.mapped("picking_ids").filtered(
            lambda p: p.picking_type_subcode == "PICK"
        )
        # Add the move for the additional product into the picking and process
        # the picking...
        pick.action_confirm()
        pick.action_assign()
        for pack_op in pick.pack_operation_ids:
            pack_op.qty_done = pack_op.product_qty
        pick.action_done()
        ship = sale.mapped("picking_ids").filtered(
            lambda p: p.picking_type_code == "outgoing"
        )
        ship.action_confirm()
        ship.action_assign()
        for pack_op in ship.pack_operation_ids:
            pack_op.qty_done = pack_op.product_qty
        ship.action_done()

        self.assertEqual(sale.order_line.qty_delivered, 1)

    def test_02(self):
        """
        Test case:
            Create and confirm a SO with product_additional
            Confirm the picking (required to get the additional product into the picking)
        Expected result:
            The moves for the additional product are linked to a warehouse...

        """
        sale = self._confirm_sale_order(products=[self.main_product])
        pick = sale.mapped("picking_ids").filtered(
            lambda p: p.picking_type_subcode == "PICK"
        )
        # Add the move for the additional product into the picking...
        pick.action_confirm()
        pick.action_assign()
        # Check that the additional product is taken into account after confirmation
        additional_move = pick.move_lines.filtered(
            lambda m, product=self.additional_product: m.product_id == product
        )
        self.assertEqual(additional_move.warehouse_id, self.warehouse_1)
        ship = sale.mapped("picking_ids").filtered(
            lambda p: p.picking_type_code == "outgoing"
        )
        additional_move = ship.move_lines.filtered(
            lambda m, product=self.additional_product: m.product_id == product
        )
        self.assertEqual(additional_move.warehouse_id, self.warehouse_1)
