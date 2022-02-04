# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _

from odoo.addons.alc_shopfloor_stock_reserve.models.stock_pack_operation import (
    NoReserveLocationError,
)
from odoo.addons.component.core import Component


class LocationContentTransfer(Component):
    _inherit = "shopfloor.location.content.transfer"

    def _create_moves_from_location(self, location):
        moves = super(LocationContentTransfer, self)._create_moves_from_location(
            location
        )
        if self.work.menu.preserve_origin_location_kind:
            if location.kind == "bin":
                moves = moves.with_context(ignore_putaway_reserve=True)
            if location.kind == "reserve":
                # The origin is a reserve -> dest must be a reserve
                dest_locations = moves.mapped("location_dest_id")
                reseve_map = {}
                for loc in dest_locations.filtered(lambda l: l.kind != "reserve"):
                    reserve_loc = loc.get_location_reserve()
                    if not reserve_loc:
                        raise NoReserveLocationError(
                            _("No reserve location associated with location %s.")
                        )
                    reseve_map[loc] = reserve_loc
                for move in moves:
                    reserve_loc = reseve_map.get(move.location_dest_id)
                    if reserve_loc:
                        move.location_dest_id = reseve_map[move.location_dest_id]
        return moves
