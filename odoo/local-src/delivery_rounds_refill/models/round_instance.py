# -*- coding: utf-8 -*-
# Copyright 2019 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


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
            "SELECT ri.id "
            "FROM round_instance ri "
            ", LATERAL ( "
            "  SELECT FROM stock_move AS m "
            "  JOIN stock_picking p ON p.id = m.picking_id "
            "  , LATERAL ( "
            "    SELECT distinct on (sq.id) sq.id "
            "    FROM stock_quant sq "
            "    LEFT JOIN stock_location sl ON sq.location_id = sl.id "
            "    WHERE sq.product_id=m.product_id "
            "    AND sq.qty > 0 "
            "    AND sl.kind = 'reserve' "
            "  ) AS ex2 "
            "  WHERE (m.state = 'confirmed' OR m.partially_available) "
            "  AND p.delivery_round_id=ri.id "
            "  LIMIT 1 "
            ") AS ex1 "
            "WHERE state IN ('draft','close') "
            "AND ri.id IN %s "
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

    @api.multi
    def open_pending_reassort(self):
        with_pending = self.filtered('has_pending_reassort')
        # compute products which are in unavailable moves in the pickings of
        # the rounds: this is quick and we can use them as a filter for the
        # reassort report
        unavailable_products_query = (
            "SELECT p.id "
            "FROM product_product p "
            "JOIN stock_move sm ON ( "
            "    p.id = sm.product_id "
            "    AND sm.state = 'confirmed' "
            ")"
            "JOIN stock_picking sp ON (sm.picking_id = sp.id) "
            "JOIN stock_picking_type spt ON (spt.id = sp.picking_type_id AND spt.code = 'internal') "
            "JOIN round_instance ri ON (sp.delivery_round_id = ri.id) "
            "WHERE ri.id in %s"
        )
        if with_pending:
            self.env.cr.execute(
                unavailable_products_query, (tuple(with_pending.ids),)
            )
            unavailable_product_ids = [
                row[0] for row in self.env.cr.fetchall()
            ]
        else:
            unavailable_product_ids = []
        domain = [('product_id', 'in', unavailable_product_ids)]
        action = self.env.ref(
            'delivery_rounds_refill.action_report_stock_refill_reassort'
        ).read()[0]
        action['domain'] = domain
        return action
