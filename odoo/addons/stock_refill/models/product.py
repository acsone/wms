# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Jacques-Etienne Baudoux <je@bcim.be>
#    Copyright 2016-2017 BCIM sprl, Camptocamp
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

from odoo import api, fields, models

import odoo.addons.decimal_precision as dp


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.multi
    def _get_domain_locations(self):
        """ Add possibility to filter by kind of location when
        computing qty_available
        """
        loc_domain = super(ProductProduct, self)._get_domain_locations()
        kind = self._context.get("loc_kind")
        if kind:
            loc_domain = (
                ["&", ("location_id.kind", "=", kind)] + loc_domain[0],
                ["&", ("location_id.kind", "=", kind)] + loc_domain[1],
                ["&", ("location_id.kind", "=", kind)] + loc_domain[2],
            )
        return loc_domain

    qty_in_parking = fields.Float(
        "Qty in parking",
        digits=dp.get_precision("Product Unit of Measure"),
        compute="_compute_qty_in_parking",
    )
    qty_in_reserve = fields.Float(
        "Qty in reserve",
        digits=dp.get_precision("Product Unit of Measure"),
        compute="_compute_qty_in_reserve",
    )
    qty_in_bin = fields.Float(
        "Qty in bins",
        digits=dp.get_precision("Product Unit of Measure"),
        compute="_compute_qty_in_bin",
    )

    def _compute_qty_in_parking(self):
        _self = self.with_context(loc_kind="parking")
        qties = {r.id: r.qty_available or 0 for r in _self}
        for rec in self:
            rec.qty_in_parking = qties[rec.id]

    def _compute_qty_in_reserve(self):
        _self = self.with_context(loc_kind="reserve")
        qties = {r.id: r.qty_available or 0 for r in _self}
        for rec in self:
            rec.qty_in_reserve = qties[rec.id]

    def _compute_qty_in_bin(self):
        _self = self.with_context(loc_kind="bin")
        qties = {r.id: r.qty_available or 0 for r in _self}
        for rec in self:
            rec.qty_in_bin = qties[rec.id]
