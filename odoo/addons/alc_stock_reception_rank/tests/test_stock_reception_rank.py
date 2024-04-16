# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from .common import CommonTestStockReceptionRankCase


class TestStockReceptionRank(CommonTestStockReceptionRankCase):
    def test_01_stock_reception_rank(self):
        """
        Test the stock reception rank when there is no delivery order.

        In this case we check that the count_partners_waiting_for_reception
        and count_products_waiting_for_reception are set to 0 since there
        are no delivery orders waiting for this product
        """
        self.assert_no_waiting()

    def test_02_stock_reception_rank(self):
        """Test the stock reception rank when there is a delivery order."""
        self.assert_no_waiting()
        self._create_outgoing_picking(self.customer1)
        self.incoming_picking.button_rank_recompute()
        self.assertEqual(self.incoming_picking.count_partners_waiting_for_reception, 1)
        self.assertEqual(self.incoming_picking.count_products_waiting_for_reception, 1)
        self.assertEqual(
            self.incoming_picking.count_planned_partners_waiting_for_reception, 0
        )
        self.assertEqual(
            self.incoming_picking.count_planned_products_waiting_for_reception, 0
        )

    def test_03_stock_reception_rank(self):
        """Test the stock reception rank when there are several delivery orders."""
        self.assert_no_waiting()
        self._create_outgoing_picking(self.customer1)
        self._create_outgoing_picking(self.customer2, qty=2)
        self.incoming_picking.button_rank_recompute()
        self.assertEqual(self.incoming_picking.count_partners_waiting_for_reception, 2)
        self.assertEqual(self.incoming_picking.count_products_waiting_for_reception, 1)
        self.assertEqual(
            self.incoming_picking.count_planned_partners_waiting_for_reception, 0
        )
        self.assertEqual(
            self.incoming_picking.count_planned_products_waiting_for_reception, 0
        )

    def test_04_stock_reception_rank(self):
        """
        Test the stock reception rank when there are several delivery orders.

        for several products
        """

        # at this stage we have 2 delivery orders waiting for reception
        # the first one for 1 product and 1 partner (incoming_picking created
        # in setUpClass) and the second one for 2 product and 2 partners
        self.env.flush_all()
        self.assert_no_waiting(self.incoming_picking_2_products)
        self._create_outgoing_picking(self.customer1, qty=1, product=self.product)
        self._create_outgoing_picking(self.customer2, qty=2, product=self.product2)
        (
            self.incoming_picking_2_products | self.incoming_picking
        ).button_rank_recompute()
        self.assertEqual(
            self.incoming_picking_2_products.count_partners_waiting_for_reception,
            2,
        )
        self.assertEqual(
            self.incoming_picking_2_products.count_products_waiting_for_reception,
            2,
        )

        self.assertEqual(
            self.incoming_picking_2_products.count_planned_partners_waiting_for_reception,
            0,
        )
        self.assertEqual(
            self.incoming_picking_2_products.count_planned_products_waiting_for_reception,
            0,
        )
        self.assertEqual(self.incoming_picking.count_partners_waiting_for_reception, 1)
        self.assertEqual(self.incoming_picking.count_products_waiting_for_reception, 1)
        self.assertEqual(
            self.incoming_picking.count_planned_partners_waiting_for_reception, 0
        )
        self.assertEqual(
            self.incoming_picking.count_planned_products_waiting_for_reception, 0
        )

    def test_05_stock_reception_rank(self):
        """
        Test the stock reception rank when there are several delivery orders.

        for several products but one partner is in both delivery orders
        """
        self._create_outgoing_picking(self.customer1, qty=1, product=self.product)
        self._create_outgoing_picking(self.customer1, qty=2, product=self.product2)
        self.incoming_picking_2_products.button_rank_recompute()
        self.assertEqual(
            self.incoming_picking_2_products.count_partners_waiting_for_reception,
            1,
        )
        self.assertEqual(
            self.incoming_picking_2_products.count_products_waiting_for_reception,
            2,
        )
        self.assertEqual(
            self.incoming_picking_2_products.count_planned_partners_waiting_for_reception,
            0,
        )
        self.assertEqual(
            self.incoming_picking_2_products.count_planned_products_waiting_for_reception,
            0,
        )

    def test_06_stock_reception_rank(self):
        """
        Test the stock reception rank is computed when a grn is assigned.

        to a picking
        """
        self._create_outgoing_picking(self.customer1, qty=1, product=self.product)
        self.assert_no_waiting(self.incoming_picking)

        # we create a grn
        self.env["stock.grn"].create(
            {
                "carrier_id": self.supplier.id,
                "delivery_note_supplier_number": "GRN RECEPTION RANK TEST",
                "picking_ids": [
                    (4, self.incoming_picking.id),
                ],
            }
        )
        self.assertEqual(self.incoming_picking.count_partners_waiting_for_reception, 1)
        self.assertEqual(self.incoming_picking.count_products_waiting_for_reception, 1)
        self.assertEqual(
            self.incoming_picking.count_planned_partners_waiting_for_reception, 0
        )
        self.assertEqual(
            self.incoming_picking.count_planned_products_waiting_for_reception, 0
        )

    def test_07_stock_reception_rank(self):
        """Test the stock reception rank is computed when cron run."""

        self._create_outgoing_picking(self.customer1, qty=1, product=self.product)
        self.assert_no_waiting(self.incoming_picking)
        self.env["stock.grn"].create(
            {
                "carrier_id": self.supplier.id,
                "delivery_note_supplier_number": "GRN RECEPTION RANK TEST",
                "picking_ids": [
                    (4, self.incoming_picking.id),
                ],
            }
        )
        self._create_outgoing_picking(self.customer2, qty=1, product=self.product)
        self.assertEqual(self.incoming_picking.count_partners_waiting_for_reception, 1)
        self.env["stock.picking"]._cron_reception_rank_recompute()
        self.assertEqual(self.incoming_picking.count_partners_waiting_for_reception, 2)
        self.assertEqual(
            self.incoming_picking.count_planned_partners_waiting_for_reception, 0
        )
        self.assertEqual(
            self.incoming_picking.count_planned_products_waiting_for_reception, 0
        )

    def test_08_stock_reception_rank(self):
        """Test the stock reception rank value."""
        self._create_outgoing_picking(self.customer1, qty=1, product=self.product)
        self.incoming_picking_2_products.button_rank_recompute()
        self.assertEqual(self.incoming_picking_2_products.rank, 1 * 1000 + 1 * 1)
        self._create_outgoing_picking(self.customer2, qty=1, product=self.product)
        self.incoming_picking_2_products.button_rank_recompute()
        self.assertEqual(self.incoming_picking_2_products.rank, 2 * 1000 + 1 * 1)
        self._create_outgoing_picking(self.customer2, qty=1, product=self.product2)
        self.incoming_picking_2_products.button_rank_recompute()
        self.assertEqual(self.incoming_picking_2_products.rank, 2 * 1000 + 2 * 1)
