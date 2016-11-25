# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Jacques-Etienne Baudoux <je@bcim.be>
#    Copyright 2016 BCIM sprl, DPHI sprl, Camptocamp
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

from openerp import models


class StockLocation(models.Model):
    _inherit = 'stock.location'

    def get_putaway_strategy(self, cr, uid, location, product, context=None):
        dest_location_id = super(StockLocation, self).get_putaway_strategy(
            cr, uid, location, product, context=None) or location.id
        bin_obj = self.pool['product.stock.bin']
        bin_ids = bin_obj.search(cr, uid, [
            ('product_id', '=', product.product_tmpl_id.id),
            ('location_id', '=', dest_location_id)],
            limit=1)
        if bin_ids:
            return bin_obj.read(
                cr, uid, bin_ids[0], ['bin_location_id'],
                load='_classic_write')['bin_location_id']
        if dest_location_id != location.id:
            # case Input under Stock and fixed putaway strat. No bin found
            # under that fixed location
            return dest_location_id
        # Search on parent location (case we are in Input under Stock and we
        # want to apply stock bin mapping)
        while location.location_id:
            location = location.location_id
            bin_ids = bin_obj.search(cr, uid, [
                ('product_id', '=', product.product_tmpl_id.id),
                ('location_id', '=', location.id)],
                limit=1)
            if bin_ids:
                return bin_obj.read(cr, uid, bin_ids[0], ['bin_location_id'],
                                    load='_classic_write')['bin_location_id']
        return dest_location_id
