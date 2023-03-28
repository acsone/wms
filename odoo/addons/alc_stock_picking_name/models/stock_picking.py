# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.addons.stock.models.stock_picking import Picking


class StockPicking(Picking):
    def name_get(self) -> list:
        """Display the name, the partner and the round."""
        res = []
        for picking in self:
            names = [picking.name]
            if picking.partner_id:
                names.append(str(picking.partner_id.display_name))
            if picking.release_channel_id:
                names.append(str(picking.release_channel_id.display_name))
            name = " - ".join(names)
            res.append((picking.id, name))
        return res
