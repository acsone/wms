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
# from openerp import _, api, exceptions, fields, models

# from datetime import datetime


class RoundInstance(models.Model):
    _name = 'round.instance'
    _order = 'date desc'

    name = fields.Char(
        'Name',
        required=True,
        # default=lambda *a: datetime.now().strftime('%y%m%d')
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
         ('open', 'Confirmed'),
         ('done', 'Done')],
        'State',
        default='draft')

    zone_ids = fields.Many2many(
        'round.zone',
        string="Zones",
        readonly=True)

    picking_ids = fields.One2many(
        'stock.picking', 'delivery_round_id', 'Pickings',
        domain=[('picking_type_subcode', '=', 'PICK')],
        )
    shipping_ids = fields.One2many(
        'stock.picking', 'delivery_round_dest_id', 'Deliveries',
        domain=[('picking_type_code', '=', 'outgoing')],
        # readonly=True,
        )

    # picking_ids = fields.One2many(
    #     'stock.picking', 'delivery_round_id', 'Deliveries',
    #     domain=[('picking_type_code', '=', 'outgoing'),
    #             ('state', '!=', 'done')])

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'round.instance') or '/'
        return super(RoundInstance, self).create(vals)

    @api.multi
    def button_zone_import(self):
        return dict(self.env.ref(
            'delivery_rounds.action_round_zone_import').read()[0])

    @api.multi
    def button_update(self):
        for zone_id in self.zone_ids:
            self._update_zone(zone_id)

    def _update_zone(self, zone_id):
        partner_ids = zone_id.partner_position_ids.mapped('partner_id.id')
        # call Try to reserve from stock the qty for confirmed pickings
        picking_confirmed = self.env['stock.picking'].search([
            ('partner_id', 'in', partner_ids),
            ('state', '=', 'confirmed')])
        picking_confirmed.action_assign()

        # retrieve all pickings (partially) available not yet bound to a delivery round
        pickings = self.env['stock.picking'].search([
            ('delivery_round_id', '=', False),
            ('partner_id', 'in', partner_ids),
            # ('state', 'in', ('confirmed', 'partially_available', 'assigned'))])
            ('state', 'in', ('partially_available', 'assigned'))])
        pickings.write({'delivery_round_id': self.id})

    def find(self, partner_id):
        import pdb;pdb.set_trace()
        # find a delivery_round for this partner otherwise create one
        zone = partner_id.round_zone_ids[0].zone_id
        instance = self.search([
            ('state', '=', 'draft'),
            ('zone_ids', 'in', zone.id),
            ])
#            ]).filtered(lambda r: zone.id in r.zone_ids.ids)
        if not instance:
            zone_ids = list(set(zone.id + zone.vehicle_id.zone_ids.ids))
            instance = self.create({
                'vehicle': zone.vehicle_id.id,
                'zone_ids': zone_ids
                })  # what date???
        return instance


class StockPicking(models.Model):
    _inherit = 'stock.picking'
    _order = 'sequence'

    sequence = fields.Integer(
        'Seq.')
    delivery_round_id = fields.Many2one(
        'round.instance', 'Round Instance Link')
    delivery_round_state = fields.Selection(
        related='delivery_round_id.state',
        store=True,
        string="Round Instance State")

    delivery_round_dest_id = fields.Many2one(
        'round.instance', 'Round Instance')

    def _get_all_from_moves(self):
        res = set()

        def _rec_add(moves):
            res.update([move.id for move in moves])
            for move in moves:
                _rec_add(move.move_orig_ids)

        for picking in self:
            moves = picking.move_lines
            _rec_add(moves)
        return list(res)

    def _get_all_dest_moves(self):
        res = set()

        def _rec_add(moves):
            res.update([move.id for move in moves])
            for move in moves:
                if move.move_dest_id:
                    _rec_add([move.move_dest_id])

        for picking in self:
            moves = picking.move_lines
            _rec_add(moves)
        return list(res)

    @api.multi
    def write(self, vals):
        if vals.get('delivery_round_id'):
            # propagate to delivery when a picking is assigned to a delivery round
            move_ids = self._get_all_dest_moves()
            moves = self.env['stock.move'].browse(move_ids)
            moves.write({'delivery_round_id': vals['delivery_round_id']})
            shippings = moves.mapped('picking_id')
            #shippings.write(
            #    {'delivery_round_dest_id': vals['delivery_round_id']})
            # ensure all related pickings are assigned to the same delivery round
            import pdb;pdb.set_trace()
            pickings = shippings._get_all_from_moves() & shippings
            pickings.write(
                {'delivery_round_dest_id': vals['delivery_round_id']})
        if 'sequence' in vals:
            # when we set a sequence on a delivery, we copy that value on the pickings
            shippings = self.filtered(
                lambda r: r.picking_type_code == 'outgoing')
            rounds = shippings.mapped('delivery_round_dest_id')
            for ri in rounds:
                pickings = ri.picking_ids.filtered(
                    lambda r: r.partner_id.id in shippings.mapped(
                        'partner_id.id'))
                pickings.write({'sequence': vals['sequence']})
        return super(StockPicking, self).write(vals)


class StockMove(models.Model):
    _inherit = 'stock.move'

    delivery_round_id = fields.Many2one(
        'round.instance', 'Round Instance',
        readonly=True)
