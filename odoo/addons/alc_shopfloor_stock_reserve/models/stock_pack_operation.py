# -*- coding: utf-8 -*-
# Copyright 2020 Camptocamp SA (http://www.camptocamp.com)
# Copyright 2021 ACSONE SA/NV (https://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import _, models
from odoo.exceptions import UserError


class StockPackOperation(models.Model):
    _inherit = "stock.pack.operation"

    def _to_reserve(self):
        """
        Recompute the location_dest_it to put the related items into a reserve
        location

        """
        self.ensure_one()
        moves = self.linked_move_operation_ids.mapped("move_id")
        dest_reserve_location = self.location_dest_id.get_location_reserve()
        if not dest_reserve_location:
            raise NoReserveLocationError(
                _("No reserve location associated with location %s.")
            )
        location_dest_id = dest_reserve_location.get_putaway_strategy(
            moves[0].mapped("product_id")
        )
        # in >= 13 the following logic should be supported by the putaway
        # strategy on the stock location
        putaway_location_dest_id = self.env["stock.location"].browse(location_dest_id)
        # give a chance to get an other reserve location from the putaway strategy
        # if the result is not a reserve we keep the original reserve location
        dest_reserve_location = (
            putaway_location_dest_id
            if putaway_location_dest_id.kind == "reserve"
            else dest_reserve_location
        )
        vals = {
            "product_id": self.product_id.id,
            "package_id": self.package_id.id,
            "picking_id": self.picking_id.id,
            "location_dest_id": dest_reserve_location.id,
        }
        # apply storage_type strategy by hand since it's not applied
        self._finalize_pack_putaway_strategy(vals)
        self.write({"location_dest_id": vals["location_dest_id"]})
        # set the initial reserve on the location to allows to select
        # an alternative reserve by the operator
        moves.write({"location_dest_id": dest_reserve_location.id})


class NoReserveLocationError(UserError):
    pass
