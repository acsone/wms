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
        query = (
            "WITH reassort_product AS "
            "(SELECT product_id FROM report_stock_refill_reassort "
            "WHERE refill_priority_reassort >= 1000) "
            "SELECT ri.id "
            "FROM round_instance AS ri "
            "WHERE EXISTS "
            "  (SELECT m.id "
            "   FROM stock_move AS m "
            "   JOIN stock_picking p on (p.id = m.picking_id) "
            "   JOIN reassort_product AS rp ON (m.product_id = rp.product_id) "
            "   WHERE p.delivery_round_id=ri.id "
            "     AND (m.state = 'confirmed' OR m.partially_available) "
            "  ) "
            "AND ri.state in ('draft', 'close') AND ri.id in %s;"
        )
        if self:
            self.env.cr.execute(query, (tuple(self.ids),))
            with_pending_refill = []
            for (id,) in self.env.cr.fetchall():
                with_pending_refill.append(id)
            with_pending_refill = set(with_pending_refill)
            for rec in self:
                rec.has_pending_reassort = rec.id in with_pending_refill

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
