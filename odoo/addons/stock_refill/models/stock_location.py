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
from odoo.exceptions import Warning


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

    def _get_ancestors(self):
        """ This method return the list of all parent locations excluding self
        """
        self._cr.execute(
            """
            SELECT distinct c.id
            FROM """
            + self._table
            + " p, "
            + self._table
            + """ c
            WHERE c.parent_left < p.parent_left
              AND c.parent_right > p.parent_right
              AND p.id in %s""",
            (tuple(self.ids),),
        )
        res = self._cr.fetchall()
        return self.browse(map(lambda x: x[0], res))

    def get_putaway_strategy(self, product):
        location = self
        location_dest = self.browse(
            super(StockLocation, self).get_putaway_strategy(product) or location.id
        )

        # check if bin location
        if location_dest.kind != "bin":
            return location_dest.id

        # Do not put product in bin if lot tracking (possibly fefo) and
        # there is already stock in reserve
        if product.tracking == "lot" and product.qty_in_reserve > 0:
            reserve = location_dest.reserve_location_id
            if not reserve:
                reserve = location_dest._get_ancestors().mapped("reserve_location_id")[
                    :1
                ]
            if not reserve:
                raise Warning(
                    _(
                        "Product %s must be put in reserve but cannot "
                        "find a suitable location"
                    )
                    % product.display_name
                )
            return reserve.id
        return super(StockLocation, self).get_putaway_strategy(product) or location.id
