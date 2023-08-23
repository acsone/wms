# Copyright 2020 Camptocamp SA (http://www.camptocamp.com)
# Copyright 2021 ACSONE SA/NV (https://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import _
from odoo.exceptions import UserError

from odoo.addons.stock.models.stock_move_line import StockMoveLine as StockMoveLineBase


class StockPackOperation(StockMoveLineBase):
    def _to_reserve(self):
        """
        Recompute the location_dest_it to put the related items into a reserve.

        location
        """
        self.ensure_one()
        putaway_location_dest_id = self.location_dest_id._get_putaway_strategy(
            self.product_id
        )
        if putaway_location_dest_id == self.location_dest_id:
            raise NoReserveLocationError(
                _(
                    "No reserve location associated with location %s.",
                    self.location_dest_id,
                )
            )
        if self.package_level_id:
            # the package level was created based on the original dest location
            # need to be removed
            self.package_level_id.explode_package()
        self.location_dest_id = putaway_location_dest_id
        self.move_id.location_dest_id = putaway_location_dest_id
        # Give high priority to this line, so it will be proposed first to the user
        self.shopfloor_priority = 1


class NoReserveLocationError(UserError):
    pass
