# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Jacques-Etienne Baudoux <je@bcim.be>
#    Copyright 2016 BCIM sprl, Camptocamp
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

from odoo import _, fields, models
from odoo.exceptions import UserError


class StockLocation(models.Model):
    _inherit = "stock.location"

    kind = fields.Selection(
        [("reserve", "Reserve"), ("parking", "Parking"), ("bin", "Bin")], string="Kind"
    )

    reserve_location_id = fields.Many2one(
        "stock.location",
        "Reserve",
        domain=[("kind", "=", "reserve")],
        help="Destination for putaway strategy when the poduct must be stored "
        "in reserve",
    )

    def get_location_reserve(self):
        self.ensure_one()
        if self.reserve_location_id:
            return self.reserve_location_id

        parent_location = self.search(
            [("id", "parent_of", self.id), ("reserve_location_id", "!=", None)],
            order="parent_left DESC",
            limit=1,
        )

        return parent_location.reserve_location_id

    def get_putaway_strategy(self, product):
        location = self
        location_dest = self.browse(
            super(StockLocation, self).get_putaway_strategy(product) or location.id
        )

        # check if bin location
        if location_dest.kind != "bin":
            return location_dest.id

        # Do not put product in bin if there is already stock in reserve
        if product.qty_in_reserve > 0:
            reserve = location_dest.get_location_reserve()
            if not reserve:
                raise UserError(
                    _(
                        "Product %s must be put in reserve but cannot "
                        "find a suitable location"
                    )
                    % product.display_name
                )
            return reserve.id
        return super(StockLocation, self).get_putaway_strategy(product) or location.id
