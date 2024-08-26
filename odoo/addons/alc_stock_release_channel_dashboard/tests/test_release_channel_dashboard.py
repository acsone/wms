# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.addons.stock_release_channel.tests.common import ChannelReleaseCase


class AlcReleaseChannelDashboard(ChannelReleaseCase):
    def test_picking_scheduled_date(self):
        """
        There are three pickings that should be assigned to release channel.

        with three different partners.

        For picking 1, holidays have been setup today, so, it should have
        two pickings in the channel after assignation.
        """
        self._update_qty_in_location(self.loc_bin1, self.product1, 20.0)
        self._update_qty_in_location(self.loc_bin1, self.product2, 20.0)

        self.assertEqual(self.channel.count_picking_release_ready, 3)
        self.assertEqual(self.channel.count_move_release_ready, 6)
