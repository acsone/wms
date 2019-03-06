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

from odoo import fields, models


class ProductPutaway(models.Model):
    _inherit = 'product.putaway'

    fixed_location_id = fields.Many2one(
        'stock.location',
        string='Default Fixed Location',
        help="Destination fixed location when no fixed location is defined "
        "for a product category",
    )

    def putaway_apply(self, product):
        res = super(ProductPutaway, self).putaway_apply(product)
        if self.method == 'fixed':
            if not res:
                return self.fixed_location_id.id
        return res
