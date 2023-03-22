# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class StockLocation(models.Model):

    _inherit = "stock.location"

    @api.model
    def name_search(self, name="", args=None, operator="ilike", limit=100):
        args = args or []
        result = super().name_search(
            name=name, args=args, operator=operator, limit=limit
        )
        if limit and len(result) < limit:
            limit_available = limit - len(result)
            eids = [x[0] for x in result]
            domain = [("barcode", operator, name), ("id", "not in", eids)] + args
            locations = self.search(domain, limit=limit_available)
            result += locations.name_get()
        return result
