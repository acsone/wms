# -*- coding: utf-8 -*-
# Copyright 2019 Camptocamp
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class RoundInstance(models.Model):
    _inherit = "round.instance"

    has_pending_reassort = fields.Boolean(
        string="Has Pending Reassort",
        compute="_compute_has_pending_reassort",
        search="_search_has_pending_reassort",
        help="True if there are some moves in the round which are waiting "
        "availability, and for which there is a pending reassort. Delivery "
        "rounds which are not in state Open are considered as not having "
        "pending reassorts.",
    )

    def _compute_has_pending_reassort(self):
        query = (
            "SELECT ri.id "
            "FROM round_instance ri "
            ", LATERAL ( "
            "  SELECT FROM stock_picking AS sp "
            "  , LATERAL ( "
            "    SELECT FROM stock_move AS sm "
            "    , LATERAL ( "
            "      SELECT distinct on (sq.product_id) sq.id "
            "      FROM stock_quant sq "
            "      WHERE sq.product_id=sm.product_id "
            "      AND sq.qty > 0 "
            "      AND sq.location_kind = 'reserve' "
            "    ) AS ex3 "
            "    WHERE sm.picking_id = sp.id "
            "    AND sm.priority > '0' "
            "    AND sm.procure_method = 'make_to_stock' "
            "    AND (sm.state = 'confirmed' OR "
            "      (sm.state = 'assigned' and sm.partially_available)) "
            "    LIMIT 1 "
            "  ) AS ex2 "
            "  WHERE sp.picking_type_subcode = 'PICK' "
            "  AND sp.delivery_round_id=ri.id "
            "  AND sp.state not in ('done', 'cancel')"
            "  LIMIT 1 "
            ") AS ex1 "
            "WHERE state IN ('draft','close') "
            "AND ri.id IN %s "
        )
        if self:
            self.env.cr.execute(query, (tuple(self.ids),))
            with_pending_refill = []
            for (id_,) in self.env.cr.fetchall():
                with_pending_refill.append(id_)
            with_pending_refill = set(with_pending_refill)
            for rec in self:
                rec.has_pending_reassort = rec.id in with_pending_refill

    def _search_has_pending_reassort(self, operator, value):
        if operator == "!=":
            value = not value
        elif operator != "=":
            raise ValueError(
                'unexpected domain (we only support "=" and "!="): '
                '("has_pending_reassort", "%s", "%s")' % (operator, value)
            )
        rounds = self.search([("state", "in", ("draft", "close"))])
        rounds = rounds.filtered("has_pending_reassort")
        if value:
            operator = "in"
        else:
            operator = "not in"
        return [("id", operator, rounds.ids)]

    @api.multi
    def open_pending_reassort(self):
        with_pending = self.filtered("has_pending_reassort")
        # compute products which are in unavailable moves in the pickings of
        # the rounds: this is quick and we can use them as a filter for the
        # reassort report
        unavailable_products_query = (
            "SELECT distinct sm.product_id "
            "FROM stock_move sm "
            "JOIN stock_picking sp ON sm.picking_id = sp.id "
            "WHERE sp.picking_type_subcode = 'PICK' "
            "  AND sm.priority > '0' "
            "  AND sm.procure_method = 'make_to_stock' "
            "  AND (sm.state = 'confirmed' OR "
            "    (sm.state = 'assigned' and sm.partially_available)) "
            "  AND sp.delivery_round_id in %s"
        )
        if with_pending:
            self.env.cr.execute(unavailable_products_query, (tuple(with_pending.ids),))
            unavailable_product_ids = [row[0] for row in self.env.cr.fetchall()]
        else:
            unavailable_product_ids = []
        domain = [("product_id", "in", unavailable_product_ids)]
        action = self.env.ref(
            "delivery_rounds_refill.action_report_stock_refill_reassort"
        ).read()[0]
        action["domain"] = domain
        return action
