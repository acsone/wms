# -*- coding: utf-8 -*-
# Copyright 2016-2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class StockLocation(models.Model):
    _inherit = 'stock.location'

    def get_putaway_strategy(self, product):
        location = self
        dest_location_id = super(StockLocation, self).get_putaway_strategy(
            product) or location.id
        bin_obj = self.env['product.stock.bin']
        lbin = bin_obj.search([
            ('product_id', '=', product.product_tmpl_id.id),
            ('location_id', '=', dest_location_id)],
            limit=1)
        if lbin:
            return lbin.bin_location_id.id
        if dest_location_id != location.id:
            # case Input under Stock and fixed putaway strat. No bin found
            # under that fixed location
            return dest_location_id
        # Do not search on parent locations, otherwise we cannot move between
        # sub-locations
        return dest_location_id
