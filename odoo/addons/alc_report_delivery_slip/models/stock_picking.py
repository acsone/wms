# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _

from odoo.addons.alc_stock_picking_parcels_and_items_per_source.models.stock_picking import (
    StockPicking as Picking,
)


class StockPicking(Picking):
    def get_numbers_per_source(self):
        """
        Return 1 dic from parcels_and_items_per_source field:

            summary = {<source_name>: {'parcels': nbr, 'items': nbr}, ...}
        """
        self.ensure_one()
        summary = {}
        for loc_id in self.parcels_and_items_per_source["locations"]:
            #  loc_id is a str in json field
            loc_id = loc_id.lower()  # because mix of 'False' and 'false' in json
            nb_parcels = self.parcels_and_items_per_source["parcels"].get(loc_id, 0)
            nb_items = self.parcels_and_items_per_source["items"].get(loc_id, 0)
            loc_name = (
                self.env["stock.location"].browse(int(loc_id)).name
                if loc_id.isdecimal()
                else _("Other")
            )
            summary[loc_name] = {"parcels": int(nb_parcels), "items": int(nb_items)}
        return summary
