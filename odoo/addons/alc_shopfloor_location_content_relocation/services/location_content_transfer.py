# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.addons.component.core import Component


class LocationContentTransfer(Component):
    _inherit = "shopfloor.location.content.transfer"

    def _create_moves_from_location(self, location):
        moves = super(LocationContentTransfer, self)._create_moves_from_location(
            location
        )
        if self.work.menu.avoid_transfer_bin_to_reserve and location.kind == "bin":
            moves = moves.with_context(ignore_putaway_reserve=True)
        return moves
