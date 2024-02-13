# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import TestDeliverProcessBase


class TestSameProductMultiSoOnePrep(TestDeliverProcessBase):
    def test_00(self):
        """
        Scenario:

        The customer orders the same product twice, in different orders.
        One preparation is created for both orders for the same product.
        """
        sale = self._confirm_sale_order(
            products=[self.main_product], qty=2, partner=self.partner2
        )
        sal2 = self._confirm_sale_order(
            products=[self.main_product], qty=2, partner=self.partner2
        )
        out1 = self._get_picking_ship(sale)
        out2 = self._get_picking_ship(sal2)
        self.assertEqual(out1, out2)
        # open the channel, pick must be generated
        self.channel.action_unlock()
        pick = self._get_picking_pick(sale)
        pick2 = self._get_picking_pick(sal2)
        # pickings are equal
        self.assertEqual(pick, pick2)
        moves = pick.move_ids.filtered(lambda m: m.product_id == self.main_product)
        self.assertEqual(len(moves), 1)
        move_line = pick.move_line_ids.filtered(
            lambda ml: ml.product_id == self.main_product
        )

        self.assertEqual(len(move_line), 1)
