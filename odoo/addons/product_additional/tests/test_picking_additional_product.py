# -*- coding: utf-8 -*-


from . import common


class TestStockPicking(common.StockPickingTestCase):
    @classmethod
    def setUpClass(cls):
        super(TestStockPicking, cls).setUpClass()
        cls.StockPicking = cls.env["stock.picking"]

        cls.location_id = cls.env.ref("stock.stock_location_stock").id
        cls.location_dest_id = cls.env.ref("stock.stock_location_customers").id

        cls.product_uom_id = cls.env.ref("product.product_uom_unit").id

    def test_pick_and_ship(self):
        sale = self._confirm_sale_order(product=self.main_product)

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

        # Check the additional product is taken into account after confirmation
        self.assertEqual(len(pick.move_lines), 2)
        self.assertEqual(len(pick.pack_operation_ids), 2)

        self.assertEqual(
            pick.mapped("pack_operation_ids.product_id"),
            self.main_product | self.additional_product,
        )

        # Check the additional product is taken into account after confirmation
        # self.assertEqual(len(ship.move_lines), 2)
