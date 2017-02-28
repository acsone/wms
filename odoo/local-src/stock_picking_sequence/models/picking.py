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

from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'
    _order = "priority desc, sequence desc, date asc, id desc"

    sequence = fields.Integer(
        'Seq.', default=-1,
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})

    @api.multi
    def write(self, vals):
        if 'sequence' in vals:
            # when we set a sequence on a delivery, we copy that value on the
            # pickings
            shippings = self.filtered(
                lambda r: r.picking_type_code == 'outgoing')
            rounds = shippings.mapped('delivery_round_id')
            for ri in rounds:
                pickings = ri.picking_ids.filtered(
                    lambda r: r.partner_id.id in shippings.mapped(
                        'partner_id.id'))
                pickings.write({'sequence': vals['sequence']})
        return super(StockPicking, self).write(vals)

    @api.multi
    def button_priority_recompute(self):
        pass
