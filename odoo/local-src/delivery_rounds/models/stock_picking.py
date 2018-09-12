# -*- coding: utf-8 -*-
# © 2016-2017 Jacques-Etienne Baudoux (BCIM)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
from collections import defaultdict

from odoo import api, fields, models
from odoo.exceptions import Warning as UserError
from odoo.addons.queue_job.job import job

_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    delivery_round_customer_id = fields.Many2one(
        'round.instance.customer', 'Delivery Round Customer', copy=False)
    delivery_round_id = fields.Many2one(
        related='delivery_round_customer_id.delivery_round_id',
        string='Delivery Round',
        store=True,
        readonly=True)

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
        return super(StockPicking, self.with_context(round_backorder=True))\
            ._create_backorder(backorder_moves)

    delivery_round_state = fields.Selection(
        related='delivery_round_id.state',
        store=True,
        string="Delivery Round State")

    def _get_all_src_pickings(self):
        def _descend_moves(lvl):
            next_lvl = lvl.mapped('move_orig_ids')
            if next_lvl:
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
    @api.constrains('delivery_round_customer_id')
    def _update_delivery_round(self):
        if self.env.context.get('noround_write'):
            return
        delivery_round_customer = self.mapped('delivery_round_customer_id')
        assert len(delivery_round_customer) <= 1, \
            'Max 1 delivery round customer can be written at a time'
        if not delivery_round_customer:
            _logger.debug("Delivery round customer unset on pickings %s",
                          self.ids)
            # unreserve quants when picking is disconnected from a delivery
            # round
            self.do_unreserve()
        else:
            if not self.env.context.get('round_assigned'):
                raise UserError(
                    "Delivery round assigned to a picking without "
                    "reservation. Method _assign_pickings on delivery.round "
                    "should have been called.")

    @api.model
    def _group_delivery_round(self, ids, domain, **kwargs):
        instances = self.env['round.instance'].search(
            [('state', 'in', ('draft', ))]).name_get()
        return instances, None

    _group_by_full = {
        'delivery_round_id': _group_delivery_round,
    }

    @api.multi
    def button_delivery_round(self):
        return dict(self.env.ref(
            'delivery_rounds.action_picking_assign_delivery_round').read()[0])

    @api.multi
    def _delay_jobs_action_assign(self):
        # Group picking by partner
        pickings_by_partner = defaultdict(lambda: self.env['stock.picking'])
        for picking in self.search([('state', '=', 'confirmed')]):
            pickings_by_partner[picking.partner_id.id] |= picking

        for pickings in pickings_by_partner.values():
            pickings.with_delay()._job_action_assign()

    @api.multi
    @job(default_channel='root.action_assign')
    def _job_action_assign(self):
        moves = self.env['stock.move'].search(
            [('picking_id', 'in', self.ids),
             ('state', '=', 'confirmed'),
             ('product_uom_qty', '!=', 0.0)],
            limit=None,
            order='priority desc, date_expected asc'
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
                ',', ", 'search_default_delivery_round_state': 'open', ", 1)
        return res
