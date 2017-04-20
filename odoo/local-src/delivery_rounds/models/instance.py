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

import math

from odoo import api, fields, models


def float2time(value):
    hour = math.floor(value)
    minute = round((value % 1) * 60)
    if (minute == 60):
        minute = 0
        hour = hour + 1
    return '%d:%02d' % (hour, minute)


class RoundInstance(models.Model):
    _name = 'round.instance'
    _order = 'date desc, time asc'
    _rec_name = 'complete_name'

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

    complete_name = fields.Char(
        'Display name', readonly=True,
        compute='_get_complete_name', store=True)

    @api.multi
    @api.depends('vehicle_id', 'date', 'time')
    def _get_complete_name(self):
        for rec in self:
            rec.complete_name = '%s %s - %s' % (
                rec.date, float2time(rec.time), rec.vehicle_id.display_name)

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
        if pickings:
            pickings.write({'delivery_round_id': self.id})

    def find(self, partner_id):
        """ Find a delivery_round for this partner """
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
                        pack.qty_done = pack.product_qty
                        for plot in pack.pack_lot_ids:
                            if plot.qty_todo > 0:
                                plot.qty = plot.qty_todo
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

    @api.multi
    def print_all_deliveryslip(self):
        return self.env['report'].get_action(self.shipping_ids,
                                             'stock.report_deliveryslip')
