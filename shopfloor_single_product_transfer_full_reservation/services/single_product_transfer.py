# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component


class ShopfloorSingleProductTransfer(Component):
    _inherit = "shopfloor.single.product.transfer"

    def _get_next_move_line_to_work(self):
        move_line = super()._get_next_move_line_to_work()
        if move_line and self.work.menu.full_location_reservation:
            # we want the same product, lot, package and owner as the move line to work on,
            # but we want to get all available quantities so use strict=True
            move_line._full_location_reservation(strict=True).move_line_ids[:1]
        return move_line
