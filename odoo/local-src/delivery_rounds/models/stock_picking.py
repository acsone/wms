# -*- coding: utf-8 -*-
# © 2016-2017 Jacques-Etienne Baudoux (BCIM)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
from collections import defaultdict

from odoo import _, api, fields, models
from odoo.addons.queue_job.job import job
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    partner_itinerary_ids = fields.Many2many(
        'round.itinerary.position',
        string='Itineraries',
        help="Indicates on which itinerary this partner is",
        compute='_compute_partner_itinerary_ids',
    )

    @api.model
    def create(self, values):
        res = super(StockPicking, self).create(values)
        backorder_id = self._context.get('backorder_assign')
        if backorder_id:
            # backorder and self may have different environment, because some
            # jobs are creating new cursors -> browse with the current environment.
            backorder = self.env['stock.picking'].browse(backorder_id)
            delivery_round_customer = backorder.delivery_round_customer_id
            delivery_round = backorder.delivery_round_id
            if delivery_round:
                delivery_round._assign_pickings(res)
            res.with_context(
                round_assigned=True
            ).delivery_round_customer_id = delivery_round_customer.id

        return res

    def _compute_partner_itinerary_ids(self):
        for picking in self:
            if not (
                picking.picking_type_subcode == 'PICK'
                or picking.picking_type_code == 'outgoing'
            ):
                continue
            partner = picking.partner_id
            if partner.type == 'contact' and partner.parent_id:
                partner = partner.parent_id
            picking.partner_itinerary_ids = partner.round_itinerary_ids

    delivery_round_customer_id = fields.Many2one(
        'round.instance.customer',
        'Delivery Round Customer',
        copy=False,
        index=True,
    )
    delivery_round_id = fields.Many2one(
        related='delivery_round_customer_id.delivery_round_id',
        string='Delivery Round',
        store=True,
        readonly=True,
        track_visibility='onchange',
        index=True,
    )

    @api.model
    def default_get(self, fields_list):
        # Prevent any default value to be set for delivery round.
        # If you search in the view, then searched value is given as default
        # value in the context. Without doing this, the backorder (created by
        # copy) will get the value no matter of copy=False

        if 'delivery_round_customer_id' in fields_list:
            fields_list.remove('delivery_round_customer_id')
        return super(StockPicking, self).default_get(fields_list)

    @api.multi
    def _create_backorder(self, backorder_moves=[]):
        # Ensure backorder is not processed again
        return super(
            StockPicking, self.with_context(round_backorder=True)
        )._create_backorder(backorder_moves)

    delivery_round_launched = fields.Boolean(
        related='delivery_round_id.picking_launched',
        store=True,
        string="Delivery Round Launched",
    )

    def _get_all_src_pickings(self):
        def _descend_moves(lvl):
            next_lvl = lvl.mapped('move_orig_ids')
            if next_lvl and 'PICK' not in lvl.mapped(
                'picking_id.picking_type_subcode'
            ):
                lvl |= _descend_moves(next_lvl)
            return lvl

        moves = _descend_moves(self.mapped('move_lines'))
        return moves.mapped('picking_id')

    def _get_all_dest_pickings(self):
        def _descend_moves(lvl):
            next_lvl = lvl.mapped('move_dest_id')
            if next_lvl:
                lvl |= _descend_moves(next_lvl)
            return lvl

        moves = _descend_moves(self.mapped('move_lines'))
        return moves.mapped('picking_id')

    @api.multi
    def write(self, vals):
        unset_round = (
            'delivery_round_customer_id' in vals
            and not vals['delivery_round_customer_id']
            and not self.env.context.get('noround_write')
        )
        if unset_round:
            in_round = self.filtered(lambda p: p.delivery_round_customer_id)
        res = super(StockPicking, self).write(vals)
        if unset_round:
            # unreserve quants when picking is disconnected from a delivery
            # round
            pickings = self.filtered(
                lambda p: not p.delivery_round_customer_id and p in in_round
            )
            pickings._unassign_delivery_round()
        return res

    def _unassign_delivery_round(self):
        if any(self.mapped('printed')):
            raise UserError(
                _(
                    'You cannot unassign a delivery round from a started picking'
                )
            )
        _logger.debug("Delivery round customer unset on pickings %s", self.ids)
        self.do_unreserve()

    @api.multi
    @api.constrains('delivery_round_customer_id')
    def _update_delivery_round(self):
        if self.env.context.get('noround_write'):
            return
        delivery_round_customer = self.mapped('delivery_round_customer_id')
        assert (
            len(delivery_round_customer) <= 1
        ), 'Max 1 delivery round customer can be written at a time'
        if delivery_round_customer:
            if not self.env.context.get('round_assigned'):
                raise UserError(
                    "Delivery round assigned to a picking without "
                    "reservation. Method _assign_pickings on delivery.round "
                    "should have been called."
                )

    @api.model
    def _group_delivery_round(self, ids, domain, **kwargs):
        instances = (
            self.env['round.instance']
            .search([('state', 'in', ('draft',))])
            .name_get()
        )
        return instances, None

    _group_by_full = {'delivery_round_id': _group_delivery_round}

    def _detach_from_round(self):
        for picking in self:
            pending_moves = self.env['stock.move'].search(
                [
                    ('picking_id', '=', picking.id),
                    ('state', 'not in', ('cancel', 'done')),
                ]
            )
            if pending_moves:
                pending_moves.with_context(
                    # set no_round_assign to force reassigning the moves to a
                    # picking which is not in the same round as the picking we
                    # may be removing from the round.
                    no_round_assign=True,
                    # set backorder_assign so that a message will be generated
                    # on picking to say where the backorder was placed.
                    backorder_assign=picking,
                ).assign_picking()

                # make sure that empty pickings are "printed" so that their
                # state is computed as 'done'
                if not picking.move_lines:
                    picking.printed = True
        # force recomputation of state, as there is no trigger on the 'printed'
        # field
        self._compute_state()

        self.filtered(lambda p: p.state not in ('cancel', 'done')).write(
            {'delivery_round_customer_id': False}
        )

    @api.multi
    def button_delivery_round(self):
        return dict(
            self.env.ref(
                'delivery_rounds.action_picking_assign_delivery_round'
            ).read()[0]
        )

    @api.multi
    def _delay_jobs_action_assign(self):
        # Group picking by partner
        pickings_by_partner = defaultdict(lambda: self.env['stock.picking'])
        pickings = self.search(
            [
                ('delivery_round_id', '=', False),
                ('state', 'not in', ('done', 'cancel')),
                ('picking_type_subcode', '=', 'PICK'),
            ]
        )
        for picking in pickings:
            pickings_by_partner[picking.partner_id] |= picking

        for partner, pickings in pickings_by_partner.iteritems():
            pickings.with_delay(
                description=_('Assign pickings of partner %s') % partner.ref,
                priority=8,
            )._job_action_assign()

    @api.multi
    @job(default_channel='root.stock_picking_assign')  # priority=8
    def _job_action_assign(self):
        moves = self.mapped('move_lines').filtered(
            lambda move: move.state not in ('done', 'cancel')
            and move.product_uom_qty > 0.0
            and not move.linked_move_operation_ids
        )
        moves.action_assign()


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    @api.multi
    def get_action_picking_tree_ready(self):
        """ Add filter for 'To Do' picking from dashboard to activate a filter
        to display only pickings linked to open delivery round """
        res = super(StockPickingType, self).get_action_picking_tree_ready()
        if self.subcode == 'PICK':
            res['context'] = res['context'].replace(
                ',', ", 'search_default_delivery_round_launched': 1, ", 1
            )
        return res
