# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.addons.shopfloor.tests.test_cluster_picking_unload import (
    ClusterPickingUnloadingCommonCase,
)
from odoo.addons.stock_location_release_channel_restriction.models.exception import (
    ReleaseChannelLocationRestrictionError,
)


class ClusterPickingSetDestinationAllCase(ClusterPickingUnloadingCommonCase):
    """Tests covering the /set_destination_all endpoint.

    All the picked lines go to the same destination, a single call to this
    endpoint set them as "unloaded" and set the destination. When the last
    available line of a picking is unloaded, the picking is set to 'done'.
    """

    def setUp(self):
        super().setUp()
        self.menu.sudo().process_picking_in_background = True

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.release_channel_1 = (
            cls.env["stock.release.channel"]
            .sudo()
            .create(
                {
                    "name": "Test Channel 1",
                }
            )
        )
        cls.release_channel_2 = (
            cls.env["stock.release.channel"]
            .sudo()
            .create(
                {
                    "name": "Test Channel 2",
                }
            )
        )
        cls.one_line_picking.release_channel_id = cls.release_channel_1
        cls.two_lines_picking.release_channel_id = cls.release_channel_2
        cls.packing_b_location.specific_release_channel_restriction = "same"
        cls.packing_a_location.specific_release_channel_restriction = "same"

    def test_set_destination_all_error(self):
        """Set destination on all lines for the full batch and end the process."""
        move_lines = self.move_lines
        # put destination packages, the whole quantity on lines and a similar
        # destination (when /set_destination_all is called, all the lines to
        # unload must have the same destination)
        self._set_dest_package_and_done(move_lines[:2], self.bin1)
        self._set_dest_package_and_done(move_lines[2:], self.bin2)
        move_lines.write({"location_dest_id": self.packing_location.id})
        self.packing_a_location.release_channel_restriction_in_move = True

        with self.assertRaises(ReleaseChannelLocationRestrictionError):
            self.service.dispatch(
                "set_destination_all",
                params={
                    "picking_batch_id": self.batch.id,
                    "barcode": self.packing_a_location.barcode,
                },
            )
