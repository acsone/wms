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


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def get_moves_by_order(self):
        self.ensure_one()

        moves_by_order = defaultdict(list)
        backorder_moves_by_order = defaultdict(list)
        result = []
        moves_witout_order = []
        backorder_moves_without_order = []
        for line in self.move_lines_related:
            if not line.order_id:
                moves_witout_order.append(line)
            else:
                moves_by_order[line.order_id].append(line)

        backorders = self.env['stock.picking']. \
            search([('backorder_id', '=', self.id)])
        for backorder in backorders:
            for line in backorder.move_lines_related:
                if not line.order_id:
                    backorder_moves_without_order.append(line)
                else:
                    backorder_moves_by_order[line.order_id].append(line)

        result_dict = {}
        for order, moves in moves_by_order.iteritems():
            result_dict[order] = [moves, backorder_moves_by_order.get(order, [])]

        if moves_witout_order:
            result.append((None, moves_witout_order, backorder_moves_without_order))

        result.extend(
            sorted(result_dict.items(),
                   key=lambda picking: (picking[0][0].date_order, picking[0][0].id))
        )
        return result
