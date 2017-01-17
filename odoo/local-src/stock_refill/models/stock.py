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

from openerp import fields, models


class ReportStockQuantBylocation(models.Model):
    _inherit = 'report.stock.quant.bylocation'
    _order = 'refill_priority desc, qty desc'

    qty_in_parking = fields.Float(
        related='product_id.qty_in_parking')
    qty_in_reserve = fields.Float(
        related='product_id.qty_in_reserve')
    qty_in_bin = fields.Float(
        related='product_id.qty_in_bin')
    outgoing_qty = fields.Float(
        related='product_id.outgoing_qty')

    def _prepare_init(self):
        d = super(ReportStockQuantBylocation, self)._prepare_init()
        d['select'] += ", product.priority_arrangement as refill_priority"
        d['groupby'] += ",priority_arrangement"
        return d

    refill_priority = fields.Integer(
        'Refill Priority', readonly=True)


class ReportStockQuantBylocationReserve(models.Model):
    _inherit = 'report.stock.quant.bylocation'
    _name = 'report.stock.quant.bylocation.reserve'
    _auto = False
    _order = 'refill_priority desc, removal_date asc, qty desc'

    def _prepare_init(self):
        d = super(ReportStockQuantBylocation, self)._prepare_init()
        d['select'] = "distinct on (product_id)" + d['select']
        d['orderby'] = "product_id"

        d['select'] += ", product.priority_reassort as refill_priority"
        d['select'] += ", lot.removal_date as removal_date"
        d['join'] += (" LEFT JOIN stock_location as location "
                      " ON quant.location_id = location.id "
                      " LEFT JOIN stock_production_lot as lot "
                      " ON quant.lot_id = lot.id ")
        d['where'] += " AND location.kind = 'reserve' "
        d['groupby'] += ", product.priority_reassort, lot.removal_date"
        return d

    refill_priority = fields.Integer(
        'Refill Priority', readonly=True)
    removal_date = fields.Datetime(
        'Removal Date',
        help="This is the date on which the goods with this Serial Number "
             "should be removed from the stock.")
