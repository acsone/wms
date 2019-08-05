# -*- coding: utf-8 -*-
# Copyright 2019 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class RoundInstance(models.Model):
    _inherit = 'round.instance'

    has_pending_reassort = fields.Boolean(
        string='Has Pending Reassort',
        compute='_compute_has_pending_reassort',
        search='_search_has_pending_reassort',
        help='True if there are some moves in the round which are waiting '
        'availability, and for which there is a pending reassort. Delivery '
        'rounds which are not in state Open are considered as not having '
        'pending reassorts.',
    )

    def _compute_has_pending_reassort(self):
        # only open rounds (state == draft) can have pending reassorts
        draft_close_recs = self.filtered(
            lambda r: r.state in ('draft', 'close')
        )
        for rec in self - draft_close_recs:
            rec.has_pending_reassort = False
        pending_reassorts = self.env['report.stock.refill.reassort'].search(
            [('refill_priority_reassort', '>', 0)]
        )
        reassort_products = pending_reassorts.mapped('product_id')
        for rec in draft_close_recs:
            # look for moves waiting availability in the delivery round, then
            # for the products of these moves check for existing replenishments
            # -> if found then the round has pending reassorts.
            moves = self.env['stock.move'].search(
                [
                    ('picking_id', 'in', rec.picking_ids.ids),
                    ('state', '=', 'confirmed'),  # waiting availability
                    ('product_id', 'in', reassort_products.ids),
                ]
            )
            if moves:
                reassorts = True
            else:
                reassorts = False
            rec.has_pending_reassort = reassorts

    def _search_has_pending_reassort(self, operator, value):
        if operator == '!=':
            value = not value
        elif operator != '=':
            raise ValueError(
                'unexpected domain (we only support "=" and "!="): '
                '("has_pending_reassort", "%s", "%s")' % (operator, value)
            )
        rounds = self.search([('state', 'in', ('draft', 'close'))])
        rounds = rounds.filtered('has_pending_reassort')
        if value:
            operator = 'in'
        else:
            operator = 'not in'
        return [('id', operator, rounds.ids)]
