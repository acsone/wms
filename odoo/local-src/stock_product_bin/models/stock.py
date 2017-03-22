# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Jacques-Etienne Baudoux <je@bcim.be>
#    Copyright 2016-2017 BCIM sprl, DPHI sprl, Camptocamp
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

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
            return lbin.read(['bin_location_id'],
                             load='_classic_write')['bin_location_id']
        if dest_location_id != location.id:
            # case Input under Stock and fixed putaway strat. No bin found
            # under that fixed location
            return dest_location_id
        # Search on parent location (case we are in Input under Stock and we
        # want to apply stock bin mapping)
        while location.location_id:
            location = location.location_id
            lbin = bin_obj.search([
                ('product_id', '=', product.product_tmpl_id.id),
                ('location_id', '=', location.id)],
                limit=1)
            if lbin:
                return lbin.read(['bin_location_id'],
                                 load='_classic_write')['bin_location_id']
        return dest_location_id
