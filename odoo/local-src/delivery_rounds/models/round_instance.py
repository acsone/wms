# -*- coding: utf-8 -*-
# © 2016-2017 Jacques-Etienne Baudoux (BCIM)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import math
from datetime import datetime

from odoo import api, fields, models, _
from odoo.exceptions import Warning as UserError

import logging
_logger = logging.getLogger(__name__)


def float2time(value):
    hour = math.floor(value)
    minute = round((value % 1) * 60)
    if (minute == 60):
        minute = 0
        hour = hour + 1
    return '%d:%02d' % (hour, minute)


def time2float(value):
    return value.hour + value.minute / 60.0


def time_now(record):
    tz_name = record._context.get('tz') or record.env.user.tz
    if not tz_name:
        raise UserError(
            "Please configure your timezone in your user preferences")
    return time2float(fields.Datetime.context_timestamp(
        record, datetime.now()))


class RoundInstance(models.Model):
    _name = 'round.instance'
    _order = 'date desc, time_picking_planned asc'
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

    time_picking_planned = fields.Float(
        'Planned Picking Start Time',
        states={'done': [('readonly', True)]},
        )
    time_leave_planned = fields.Float(
        'Planned Vehicle Start Time',
        states={'done': [('readonly', True)]},
        )

    stat_time_picking = fields.Float(
        'Picking Start Time', readonly=True)
    stat_time_leave = fields.Float(
        'Vehicle Start Time', readonly=True)

    template_id = fields.Many2one(
        'round.template', 'Template',
        states={'done': [('readonly', True)]},
        ondelete='restrict')
    color = fields.Integer(
        related='template_id.color')
    state = fields.Selection(
        [('draft', 'Draft'),
         ('open', 'Confirmed'),
         ('done', 'Done')],
        'State',
        default='draft')

    itinerary_ids = fields.Many2many(
        'round.itinerary',
        string="Itineraries",
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
        'Display Name', readonly=True,
        compute='_get_complete_name', store=True)

    @api.multi
    @api.depends('template_id', 'date', 'time_leave_planned')
    def _get_complete_name(self):
        for rec in self:
            rec.complete_name = '%s %s - %s' % (
                rec.date,
                float2time(rec.time_leave_planned),
                rec.template_id.display_name)

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'round.instance') or '/'
        return super(RoundInstance, self).create(vals)

    @api.multi
    def button_itinerary_import(self):
        return dict(self.env.ref(
            'delivery_rounds.action_round_itinerary_import').read()[0])

    @api.multi
    def button_update(self):
        for record in self:
            record._include_itinerary(self.itinerary_ids)

    def _include_itinerary(self, itineraries):
        self.ensure_one()

        self.itinerary_ids |= itineraries

        partner_ids = itineraries.mapped('partner_position_ids.partner_id.id')

        picking_confirmed = self.env['stock.picking'].search([
            ('delivery_round_id', '=', False),
            ('partner_id', 'in', partner_ids),
            ('state', '=', 'confirmed')])
        self._assign_pickings(picking_confirmed)

    def _assign_pickings(self, pickings):
        _logger.debug("Assign to delivery round %s the pickings %s",
                      self.id, pickings.ids)
        try:
            # call Try to reserve from stock the qty for confirmed pickings
            pickings.filtered(
                lambda p: p.state in ['draft', 'confirmed']).with_context(
                    round_autoset=False).action_assign()
        except UserError:
            # if no moves
            pass
        else:
            # retrieve all pickings (partially) available not yet bound to a
            # delivery round
            pickings_assigned = self.env['stock.picking'].search([
                # We need to be able to assign to another round instance
                # ('delivery_round_id', '=', False),
                ('id', 'in', pickings.ids),
                ('state', 'in', ('partially_available', 'assigned'))])
            if pickings_assigned:
                _logger.debug("Add to delivery round %s the pickings %s",
                              self.id, pickings.ids)
                partner = pickings_assigned.mapped('partner_id')
                rank = self._add_customer(partner)
                pickings_assigned.with_context(round_assigned=True).write({
                    'delivery_round_id': self.id,
                    'rank': rank})

    @api.multi
    def _add_customer(self, customer):
        self.ensure_one()
        ric = self.env['round.instance.customer'].search([
            ('delivery_round_id', '=', self.id),
            ('res_partner_id', '=', customer.id)])
        rank = 0
        if not ric:
            pos = self.env['round.itinerary.position'].search([
                ('itinerary_id', 'in', self.itinerary_ids.ids),
                ('partner_id', '=', customer.id)])
            if pos:
                rank = pos.sequence + pos.itinerary_id.sequence*1000
            ric = self.env['round.instance.customer'].create({
                'delivery_round_id': self.id,
                'res_partner_id': customer.id,
                'rank': rank,
                })
        else:
            rank = ric.rank
        return rank

    @api.multi
    def _remove_customer(self, customer):
        for rec in self:
            if not self.env['stock.picking'].search([
                    ('delivery_round_id', '=', self.id),
                    ('res_partner_id', '=', customer.id)]):
                ric = self.env['round.instance.customer'].search({
                    'delivery_round_id': self.id,
                    'res_partner_id': customer.id,
                    })
                if ric:
                    ric.unlink()

    @api.model
    def find(self, partner):
        """ Find a delivery_round for this partner """
        _logger.debug("Search a round instance for partner %s", partner.id)
        # TODO: improve: take first delivery round having a shipping for that
        # partner
        itinerary_ids = partner.round_itinerary_ids.mapped(
            'itinerary_id.id')
        if not itinerary_ids:
            return self.browse()
        return self.search([
            ('state', '=', 'draft'),
            ('itinerary_ids', 'in', itinerary_ids),
            ], limit=1)

    count_picking_available_total = fields.Integer(
        'Picking Available Total',
        compute='_get_count_picking',
        readonly=True)
    count_picking_done_total = fields.Integer(
        'Picking Done Total',
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
    def button_confirm(self):
        """ Mark as confirmed. This launch the start of the pickings
        """
        self.state = 'open'
        self.stat_time_picking = time_now(self)

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
        self.stat_time_leave = time_now(self)

    @api.multi
    def print_all_deliveryslip(self):
        return self.env['report'].get_action(self.shipping_ids,
                                             'stock.report_deliveryslip')

    @api.multi
    def unlink(self):
        pickings = self.mapped('picking_ids')
        res = super(RoundInstance, self).unlink()
        # @api.constrains is not triggered on source model when referenced
        # record is deleted. So let's call it.
        pickings._update_delivery_round()
        return res

    @api.multi
    @api.depends('shipping_ids')
    def _compute_shipping_count(self):
        for shipping in self:
            shipping.shipping_count = len(shipping.shipping_ids)

    shipping_count = fields.Integer(
        compute='_compute_shipping_count',
    )

    @api.multi
    def action_view_shippings(self):
        self.ensure_one()

        action_data = self.env.ref(
            'delivery_rounds.action_picking_tree_round'
        ).read()[0]
        action_data['domain'] = [
            ('picking_type_code', '=', 'outgoing'),
            ('delivery_round_id', '=', self.id),
        ]
        action_data['context'] = {
            'default_picking_type_code': 'outgoing',
            'default_delivery_round_id': self.id,
        }

        return action_data

    @api.multi
    @api.depends('picking_ids')
    def _compute_picking_count(self):
        for picking in self:
            picking.picking_count = len(picking.picking_ids)

    picking_count = fields.Integer(
        compute='_compute_picking_count',
    )

    @api.multi
    def action_view_pickings(self):
        self.ensure_one()

        action_data = self.env.ref(
            'delivery_rounds.action_picking_tree_round'
        ).read()[0]
        action_data['domain'] = [
            ('picking_type_subcode', '=', 'PICK'),
            ('delivery_round_id', '=', self.id),
        ]
        action_data['context'] = {
            'default_picking_type_subcode': 'PICK',
            'default_delivery_round_id': self.id,
        }
        return action_data

    instance_customer_ids = fields.One2many(
        comodel_name='round.instance.customer',
        inverse_name='delivery_round_id',
        string='Customers',
        states={'done': [('readonly', True)]},
    )


class RoundInstanceCustomer(models.Model):
    _name = 'round.instance.customer'
    _order = 'rank'

    _sql_constraints = [
        (
            'unique_instance_customer',
            'UNIQUE(delivery_round_id, res_partner_id)',
            _('The customer must be unique in a delivery round.')
        ),
    ]

    delivery_round_id = fields.Many2one(
        comodel_name='round.instance',
        string='Delivery Round',
        required=True,
        ondelete='cascade',
    )

    res_partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Customer',
        required=True,
        ondelete='restrict',
    )

    rank = fields.Integer(
        string='Rank',
    )

    @api.multi
    @api.constrains('rank')
    def _propagate_rank(self):
        for instance_customer in self:
            rank = instance_customer.rank
            # when we set a rank on a round instance customer,
            # we copy that value on the pickings
            pickings = self.delivery_round_id.shipping_ids.filtered(
                lambda p:
                p.partner_id == instance_customer.res_partner_id and
                p.rank != rank
            )
            pickings += self.delivery_round_id.picking_ids.filtered(
                lambda p:
                p.partner_id == instance_customer.res_partner_id and
                p.rank != rank
            )
            _logger.debug(
                "Rank set on round instance customer %s. Propagate to "
                "pickings and shippings %s",
                self.ids, pickings.ids)
            pickings.write({'rank': rank})
