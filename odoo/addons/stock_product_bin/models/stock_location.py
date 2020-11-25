# -*- coding: utf-8 -*-
# Copyright 2016-2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class StockLocation(models.Model):
    _inherit = "stock.location"

    def get_putaway_strategy(self, product):
        location = self
        dest_location_id = (
            super(StockLocation, self).get_putaway_strategy(product) or location.id
        )
        stock_bin_ids = product.product_tmpl_id.stock_bin_ids
        lbin = stock_bin_ids.filtered(
            lambda b, location_id=dest_location_id: b.location_id.id == location_id
        )
        if lbin:
            return lbin[0].bin_location_id.id
        if dest_location_id != location.id:
            # case Input under Stock and fixed putaway strat. No bin found
            # under that fixed location
            return dest_location_id
        # Search on parent location (case we are in Input under Stock and we
        # want to apply stock bin mapping)
        while location.act_as_view and location.location_id:
            location = location.location_id
            lbin = stock_bin_ids.filtered(lambda b, loc=location: b.location_id == loc)
            if lbin:
                return lbin[0].bin_location_id.id
        return dest_location_id
