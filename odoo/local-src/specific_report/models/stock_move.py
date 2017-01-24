# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Sylvain Van Hoof <svh@sylvainvh.be>
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
from collections import defaultdict

from openerp import models, fields, api


class StockMove(models.Model):
    _inherit = 'stock.move'

    order_line_id = fields.Many2one('sale.order.line',
                                    string='Order line',
                                    related='procurement_id.sale_line_id',
                                    store=True)
    order_id = fields.Many2one('sale.order', related='order_line_id.order_id')

    @api.multi
    def get_lots(self):
        """
        Return all lots for the stock move
        :return: Return a list of tuple
        """
        qty_by_lot = {}

        quants = filter(
            None, self.linked_move_operation_ids.mapped('reserved_quant_id'))
        for quant in quants:
            if not quant.lot_id:
                continue
            lot = quant.lot_id

            existing_qty = qty_by_lot.get(lot.name, [])
            if existing_qty:
                qty_by_lot[lot.name] = [existing_qty[0] +
                                        quant.qty, existing_qty[1]]
            else:
                qty_by_lot[lot.name] = [quant.qty, lot.life_date or '']

        result = [[key, value[0], value[1]]
                  for key, value
                  in qty_by_lot.iteritems()]

        # Sort lot by name
        return sorted(result, key=lambda lot: lot[0])
