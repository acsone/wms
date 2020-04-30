# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Jacques-Etienne Baudoux <je@bcim.be>
#    Copyright 2017 BCIM sprl, Camptocamp
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

from odoo import fields, models


class ProductPutaway(models.Model):
    _inherit = 'product.putaway'

    route_location_ids = fields.One2many(
        'stock.fixed.putaway.route.strat',
        'putaway_id',
        'Fixed Locations Per Route',
    )

    def putaway_apply(self, product):
        if self.route_location_ids:
            routes = product.route_ids + product.route_from_categ_ids
            for strat in self.route_location_ids:
                if strat.route_id in routes:
                    dest = strat.fixed_location_id
                    if dest.putaway_strategy_id:
                        return dest.putaway_strategy_id.putaway_apply(product)
                    return dest.id
        return super(ProductPutaway, self).putaway_apply(product)


class StockFixedPutawayRouteStrat(models.Model):
    _name = 'stock.fixed.putaway.route.strat'
    _order = 'sequence'

    putaway_id = fields.Many2one(
        'product.putaway', 'Put Away Method', required=True
    )
    fixed_location_id = fields.Many2one(
        'stock.location', 'Location', required=True
    )
    route_id = fields.Many2one('stock.location.route', 'Route', required=True)
    sequence = fields.Integer('Priority')
