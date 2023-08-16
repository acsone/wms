# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.shopfloor.tests.test_location_content_transfer_base import (
    LocationContentTransferCommonCase,
)


class TestCustomErrorMessage(LocationContentTransferCommonCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.picking = cls._create_picking(
            lines=[(cls.product_a, 10), (cls.product_b, 10)],
        )

        cls._fill_stock_for_moves(
            cls.picking.move_line_ids, location=cls.content_loc, in_package=True
        )
        cls.picking.action_assign()
        cls.products = cls.product_a | cls.product_b

    def test_00_trigger_custom_message_reserved_moves(self):
        """Check that it's not allowed to reserve the same quantity."""
        response = self.service.dispatch(
            "scan_location", params={"barcode": self.content_loc.barcode}
        )
        self.assert_response_start(
            response,
            message=self.msg_store.location_empty(self.content_loc),
        )
