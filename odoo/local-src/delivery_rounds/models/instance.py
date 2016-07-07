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

from openerp import _, api, exceptions, fields, models

from datetime import datetime


class RoundInstance(models.Model):
    _name = 'round.instance'

    name = fields.Char(
        'Name',
        required=True,
        #default=lambda *a: datetime.now().strftime('%y%m%d')
        default='New',
        )
    date = fields.Datetime(
        'Date',
        required=True,
        default=fields.Datetime.now)
    vehicle_id = fields.Many2one(
        'round.vehicle', 'Vehicle',
        ondelete='restrict')
    state = fields.Selection(
        [('draft', 'Draft'),
         ('open', 'Ready'),
         ('done', 'Done')],
        'State',
        default='draft')
    picking_ids = fields.One2many(
        'stock.picking', 'delivery_round_id', 'Deliveries',
        domain=[('picking_type_code', '=', 'outgoing'),
                ('state', '!=', 'done')])

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('round.instance') or '/'
        return super(RoundInstance, self).create(vals)

    @api.multi
    def button_zone_import(self):
        return dict(self.env.ref('round.action_zone_import').read()[0])



class StockPicking(models.Model):
    _inherit = 'stock.picking'

    delivery_round_id = fields.Many2one(
        'round.instance', 'Round Instance Link')
    delivery_round_dest_id = fields.Many2one(
        'round.instance', 'Round Instance')

    def _get_all_moves(self):
        res = set()

        def _rec_add(moves):
            res.update([move.id for move in moves])
            for move in moves:
                _rec_add(move.move_orig_ids)

        for picking in self:
            moves = picking.move_lines
            _rec_add(moves)
        return list(res)

    @api.multi
    def write(self, vals):
        if 'delivery_round_id' in vals:
            move_ids = self._get_all_moves()
            moves = self.env['stock.move'].browse(move_ids)
            moves.write({'delivery_round_id': vals['delivery_round_id']})
            pickings = moves.mapped('picking_id').write({'delivery_round_dest_id': vals['delivery_round_id']})
        return super(StockPicking, self).write(vals)


class StockMove(models.Model):
    _inherit = 'stock.move'

    delivery_round_id = fields.Many2one(
        'round.instance', 'Round Instance',
        readonly=True)
