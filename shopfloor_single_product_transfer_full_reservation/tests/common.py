# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.shopfloor_single_product_transfer.tests.common import (
    CommonCase as BaseCommonCase,
)


class CommonCase(BaseCommonCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.menu.sudo().allow_get_work = True
        cls.location_src_a = (
            cls.env["stock.location"]
            .sudo()
            .create(
                {
                    "name": "Source A",
                    "location_id": cls.location_src.id,
                }
            )
        )

    def _data_for_start_line(
        self, move_line, selected_location_id=None, selected_package_id=None
    ):
        return {
            "move_line": self._data_for_move_line(move_line),
            "selected_location_id": selected_location_id,
            "selected_package_id": selected_package_id,
            "scan_location_or_pack_first": self.menu.scan_location_or_pack_first,
        }

    def _find_work(self):
        """Dispatch find_work, assert the response and return the assigned move line."""
        response = self.service.dispatch("find_work")
        move_line = fields.first(self.picking_1.move_line_ids)
        data = self._data_for_start_line(move_line)
        self.assert_response(response, next_state="start_line", data=data)
        return move_line
