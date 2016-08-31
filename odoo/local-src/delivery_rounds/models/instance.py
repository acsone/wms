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
    _order = 'date desc, time asc'

    name = fields.Char(
        'Name',
        required=True,
        # default=lambda *a: datetime.now().strftime('%y%m%d')
        default='New',
        )
    date = fields.Date(
        'Date',
        required=True,
        states={'done': [('readonly', True)]},
        default=fields.Date.context_today)
    time = fields.Float(
        'Planned Time',
        states={'done': [('readonly', True)]},
        )
    vehicle_id = fields.Many2one(
        'round.vehicle', 'Vehicle',
        states={'done': [('readonly', True)]},
        ondelete='restrict')
    color = fields.Integer(
        related='vehicle_id.color')
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
        states={'done': [('readonly', True)]},
        )
    shipping_ids = fields.One2many(
        'stock.picking', 'delivery_round_id', 'Deliveries',
        domain=[('picking_type_code', '=', 'outgoing')],
        states={'done': [('readonly', True)]},
        # readonly=True,
        )

    @api.model
    @api.depends('vehicle_id', 'date', 'time')
    def name_get(self):
        res = []
        for rec in self:
            res.append((rec.id, '%s %s - %s' % (
                rec.date, rec.time, rec.vehicle_id.display_name)))
        return res

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

        # retrieve all pickings (partially) available not yet bound to a
        # delivery round
        pickings = self.env['stock.picking'].search([
            ('delivery_round_id', '=', False),
            ('partner_id', 'in', partner_ids),
            ('state', 'in', (
                # 'confirmed',
                'partially_available',
                'assigned'))])
        pickings.write({'delivery_round_id': self.id})

    def find(self, partner_id):
        """ Find a delivery_round for this partner otherwise create one """
        zone_ids = partner_id.round_zone_ids.mapped('zone_id.id')
        instance = self.search([
            ('state', '=', 'draft'),
            ('zone_ids', 'in', zone_ids),
            ], limit=1)
        if instance:
            return instance[0]
        return None  # do not automatically create new round instance
        # zone_ids = list(set(zone.id + zone.vehicle_id.zone_ids.ids))
        # instance = self.create({
        #     'vehicle': zone.vehicle_id.id,
        #     'zone_ids': zone_ids
        #     })  # what date???
        # return instance

    count_picking_available_total = fields.Integer(
        'Picking Available Total',
        compute='_get_count_picking',
        readonly=True)
    count_picking_done_total = fields.Integer(
        'Picking Donee Total',
        compute='_get_count_picking',
        readonly=True)
    count_picking_available_partner = fields.Integer(
        'Picking Available Partner',
        compute='_get_count_picking',
        readonly=True)
    count_picking_available_weight = fields.Integer(
        'Picking Available Total',
        compute='_get_count_picking',
        readonly=True)

    @api.one
    @api.depends('picking_ids')
    def _get_count_picking(self):
        self.count_picking_done_total = len(self.picking_ids.filtered(
            lambda r: r.state == ('done')))
        pickings = self.picking_ids.filtered(
            lambda r: r.state in ('partially_available', 'assigned', 'done'))
        self.count_picking_available_total = len(pickings)
        self.count_picking_available_partner = \
            len(pickings.mapped('partner_id'))
        weight = 0.0
        for pack in pickings.mapped('pack_operation_ids'):
            weight += pack.product_id.weight * pack.product_qty
        self.count_picking_available_weight = weight

    @api.multi
    def action_picking_tree_available(self):
        return dict(self.env.ref(
            'delivery_rounds.action_picking_tree_available_round').read()[0])

    @api.one
    def button_deliver(self):
        """ Validate all deliveries that are available. Mark as done and unlink
        other deliveries """
        for shipping in self.shipping_ids:
            if shipping.state in ('assigned', 'partially_available'):
                for pack in shipping.pack_operation_ids:
                    if pack.product_qty > 0:
                        pack.write({'qty_done': pack.product_qty})
                    else:
                        pack.unlink()
                shipping.do_transfer()
        self.button_done()

    @api.one
    def button_done(self):
        """ Mark as done and unlink waiting deliveries
        """
        self.state = 'done'
        for shipping in self.shipping_ids:
            if shipping.state == 'waiting':
                shipping.delivery_round_id = False


class StockPicking(models.Model):
    _inherit = 'stock.picking'
    _order = 'sequence'

    sequence = fields.Integer(
        'Seq.')
    delivery_round_id = fields.Many2one(
        'round.instance', 'Delivery Round')
    delivery_round_state = fields.Selection(
        related='delivery_round_id.state',
        store=True,
        string="Delivery Round State")

    def _get_all_from_pickings(self):
        res = set()

        def _rec_add(moves):
            res.update([move.id for move in moves])
            for move in moves:
                _rec_add(move.move_orig_ids)

        for picking in self:
            moves = picking.move_lines
            _rec_add(moves)
        return self.env['stock.move'].browse(list(res)).mapped('picking_id')

    def _get_all_dest_pickings(self):
        res = set()

        def _rec_add(moves):
            res.update([move.id for move in moves])
            for move in moves:
                if move.move_dest_id:
                    _rec_add([move.move_dest_id])

        for picking in self:
            moves = picking.move_lines
            _rec_add(moves)
        return self.env['stock.move'].browse(list(res)).mapped('picking_id')

    @api.multi
    def write(self, vals):
        if ('delivery_round_id' in vals and
                not self._context.get('noround_write')):
            # propagate to delivery when a picking is (un)assigned to a
            # delivery round
            shippings = self._get_all_dest_pickings().filtered(
                lambda r: r.picking_type_code == 'outgoing')
            # ensure all related pickings are assigned to the same delivery
            # round
            pickings = shippings._get_all_from_pickings()
            # TODO: we should ensure a picking is not already done for another
            #       delivery round
            pickings = pickings - self
            pickings = pickings.filtered(
                lambda r: r.state in (
                    'waiting',
                    'confirmed',
                    'partially_available',
                    'assigned') and
                r.delivery_round_id.id != vals['delivery_round_id'])
            pickings.with_context(noround_write=True).write(
                {'delivery_round_id': vals['delivery_round_id']})
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

    @api.model
    def _group_delivery_round(self, ids, domain, **kwargs):
        vehicle = self.env['round.instance'].search(
            [('state', 'in', ('draft', ))]).name_get()
        return vehicle, None

    _group_by_full = {
        'delivery_round_id': _group_delivery_round,
    }


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    @api.multi
    def get_action_picking_tree_ready(self):
        """ Add filter for 'To Do' picking from dashboard to activate a filter
        to display only pickings linked to open delivery round """
        res = super(StockPickingType, self).get_action_picking_tree_ready()
        if self.subcode == 'PICK':
            res['context'] = res['context'].replace(
                ',', ", 'search_default_delivery_round_state': 'open', ", 1)
        return res
