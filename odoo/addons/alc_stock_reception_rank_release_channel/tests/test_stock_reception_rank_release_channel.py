# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.alc_stock_reception_rank.tests.common import (
    CommonTestStockReceptionRankCase,
)


class TestStockReceptionRank(CommonTestStockReceptionRankCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # we create release channels
        cls.release_channel = cls.env["stock.release.channel"].create(
            {
                "name": "Release Channel",
            }
        )
        cls.release_channel2 = cls.env["stock.release.channel"].create(
            {
                "name": "Release Channel2",
            }
        )

    def test_01_stock_reception_rank(self):
        """
        The rank of the reception is increased by 1000000 for each.

        release channel where a product is waiting for availability.
        """
        self.assert_no_waiting()

        # we create a delivery order for the product and the customer
        outgoing_picking1 = self._create_outgoing_picking(self.customer1)
        outgoing_picking2 = self._create_outgoing_picking(self.customer1)
        self.incoming_picking.button_rank_recompute()
        # we check that the rank of the reception is increased by 1000000
        # for the release channel 1 customer -> 1000 + 1 product -> 1
        self.assertEqual(self.incoming_picking.rank, 1001)
        # we set the outgoing picking into a release channel
        outgoing_picking1.release_channel_id = self.release_channel
        self.incoming_picking.button_rank_recompute()
        # we check that the rank of the reception is increased by 1000000
        # 1 customer -> 1000 + 1 product -> 1 and 1 release channel -> 1000000
        self.assertEqual(self.incoming_picking.rank, 1001001)

        # we set the outgoing picking 2 into a release channel
        outgoing_picking2.release_channel_id = self.release_channel2
        self.incoming_picking.button_rank_recompute()
        self.assertEqual(self.incoming_picking.rank, 2001001)
