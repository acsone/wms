# Copyright 2023 Camptocamp SA (http://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# from odoo.tests.common import Form

from odoo.addons.shopfloor.tests.common import CommonCase


# pylint: disable=missing-return
class TestLocationContentTransferSorter(CommonCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        with cls.work_on_actions(cls) as work:
            cls.sorter = work.component(usage="location_content_transfer.sorter")
        cls.location_1 = (
            cls.env["stock.location"]
            .sudo()
            .create({"name": "Location 1", "usage": "internal"})
        )
        cls.location_2 = (
            cls.env["stock.location"]
            .sudo()
            .create({"name": "Location 2", "usage": "internal"})
        )
        cls.location_1_2 = (
            cls.env["stock.location"]
            .sudo()
            .create(
                {
                    "name": "Location 2",
                    "usage": "internal",
                    "location_id": cls.location_1.id,
                }
            )
        )
        cls.location_2_1 = (
            cls.env["stock.location"]
            .sudo()
            .create(
                {
                    "name": "Location 1",
                    "usage": "internal",
                    "location_id": cls.location_2.id,
                }
            )
        )

        cls.fake_move_line_location_1 = cls.env["stock.move.line"].new(
            {
                "location_dest_id": cls.location_1.id,
            }
        )
        cls.fake_move_line_location_2 = cls.env["stock.move.line"].new(
            {
                "location_dest_id": cls.location_2.id,
            }
        )
        cls.fake_move_line_location_1_2 = cls.env["stock.move.line"].new(
            {
                "location_dest_id": cls.location_1_2.id,
            }
        )
        cls.fake_move_line_location_2_1 = cls.env["stock.move.line"].new(
            {
                "location_dest_id": cls.location_2_1.id,
            }
        )

    def test_sort_key(self):
        """Check sorting key."""
        lines = sorted(
            [self.fake_move_line_location_2, self.fake_move_line_location_1],
            key=self.sorter._sort_key,
        )
        self.assertEqual(
            lines, [self.fake_move_line_location_1, self.fake_move_line_location_2]
        )

        # we sort on the name not on the complete name
        lines = sorted(
            [self.fake_move_line_location_1_2, self.fake_move_line_location_2_1],
            key=self.sorter._sort_key,
        )
        self.assertEqual(
            lines, [self.fake_move_line_location_2_1, self.fake_move_line_location_1_2]
        )
