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

from openerp import api, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.multi
    def write(self, vals):
        if vals.get('state') == 'assigned' or vals.get('partially_available'):
            for picking in self.mapped('picking_id'):
                if picking.picking_type_subcode == 'PICK':
                    if not picking.delivery_round_id:
                        delivery_round = self.env['round.instance'].find(
                            picking.partner_id)
                        if delivery_round:
                            picking.delivery_round_id = delivery_round
                    else:
                        # reassign to propagate values to newly created dest
                        # moves pickings
                        picking.delivery_round_id = picking.delivery_round_id
        return super(StockMove, self).write(vals)
