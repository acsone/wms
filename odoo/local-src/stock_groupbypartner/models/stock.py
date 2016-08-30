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

from openerp import api, fields, models


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    groupbypartner = fields.Boolean(
        'Use existing picking having same partner')
    groupbypartner_maxweight = fields.Integer('Max Weight')


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.cr_uid_ids_context
    def _picking_assign(self, cr, uid, move_ids, context=None):
        """Try to assign the moves to an existing picking
        that has not been reserved yet and that do not has the same
        procurement group but the same partner, locations and picking type
        (moves should already have them identical) Otherwise, create a new
        picking to Assign them to.
        """
        # FIXME TODO: does not work for MTO products.
        move = self.browse(cr, uid, move_ids, context=context)[0]
        if not move.picking_type_id.groupbypartner:
            return super(StockMove, self)._picking_assign(
                cr, uid, move_ids, context=context)
        pick_obj = self.pool.get("stock.picking")
        picks = pick_obj.search(cr, uid, [
                ('partner_id', '=', move.group_id.partner_id.id),
                ('location_id', '=', move.location_id.id),
                ('location_dest_id', '=', move.location_dest_id.id),
                ('picking_type_id', '=', move.picking_type_id.id),
                ('printed', '=', False),
                ('state', 'in', ['draft', 'confirmed', 'waiting',
                                 'partially_available', 'assigned'])
            ], limit=1, context=context)
        # check weight
        total_weight = 0.0
        pickings = self.pool['stock.picking'].browse(cr, uid, picks, context=context)
        if move.picking_type_id.groupbypartner_maxweight:
            total_weight = move.product_id.weight * move.product_qty
            for pmove in pickings.move_lines:
                total_weight += pmove.product_id.weight * pmove.product_qty
        if picks and total_weight <= move.picking_type_id.groupbypartner_maxweight:
            pick = picks[0]
        else:
            values = self._prepare_picking_assign(
                cr, uid, move, context=context)
            pick = pick_obj.create(cr, uid, values, context=context)
        res = self.write(cr, uid, move_ids, {'picking_id': pick},
                          context=context)
