# -*- coding: utf-8 -*-
# © 2016-2017 Jacques-Etienne Baudoux (BCIM)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models

import logging
_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    delivery_round_id = fields.Many2one(
        'round.instance', 'Delivery Round', copy=False)
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
    def write(self, vals):
        delivery_round_partner = {}
        partners = []
        if not vals.get('delivery_round', True):
            # Delivery round unset on picking
            for picking in self:
                delivery_round_partner.setdefault(
                    picking.delivery_round_id, set()).\
                    add(picking.partner_id)
        res = super(StockPicking, self).write(vals)
        for delivery_round, partners in delivery_round_partner.iteritems():
            for partner in partners:
                delivery_round._remove_customer(partner)
        return res

    @api.multi
    @api.constrains('delivery_round_id')
    def _update_delivery_round(self):
        if self.env.context.get('noround_write'):
            return
        delivery_round = self.mapped('delivery_round_id')
        assert len(delivery_round) <= 1, \
            'Max 1 delivery_round can be written at a time'
        if not delivery_round:
            _logger.debug("Delivery round unset on pickings %s", self.ids)
            # unreserve quants when picking is disconnected from a delivery
            # round
            self.do_unreserve()
        else:
            if not self.env.context.get('round_assigned'):
                _logger.warn(
                    "Delivery round assigned to a picking without "
                    "reservation. Method _assign_pickings on delivery.round "
                    "should have been called.")
            # propagate to delivery when a picking is (un)assigned to a
            # delivery round
            shippings = self._get_all_dest_pickings().filtered(
                lambda r: r.picking_type_code == 'outgoing')
            # ensure all related pickings are assigned to the same delivery
            # round
            pickings = shippings._get_all_src_pickings()
            # TODO: we should ensure a picking is not already done for another
            #       delivery round
            pickings = pickings.filtered(
                lambda r: r.state in (
                    'waiting',
                    'confirmed',
                    'partially_available',
                    'assigned') and
                r.delivery_round_id.id != delivery_round.id)
            # if not pickings:
            #     raise Warning(_(
            #         'No available picking to assign this delivery round'))
            if pickings:
                _logger.debug(
                    "Delivery round %s set on pickings %s. Propagate "
                    "to group %s",
                    delivery_round.id, self.ids, pickings.ids)
                for partner in self.mapped('partner_id'):
                    rank = delivery_round._add_customer(partner)
                    pickings.with_context(noround_write=True).write({
                        'delivery_round_id': delivery_round.id,
                        'rank': rank})
            _logger.debug(
                "Delivery round %s set on pickings %s. Done.",
                delivery_round.id, self.ids)

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
