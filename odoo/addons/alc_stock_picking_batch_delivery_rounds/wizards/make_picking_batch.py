# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from psycopg2.extensions import AsIs

from odoo import _, api, models
from odoo.exceptions import ValidationError


class MakePickingBatch(models.TransientModel):

    _inherit = "make.picking.batch"

    def _get_delivery_rounds_candidates(self, domain, user):
        query = """
            SELECT sp.id, ri.id FROM stock_picking sp
                JOIN round_instance ri ON sp.delivery_round_id = ri.id
                WHERE sp.picking_type_subcode = 'PICK'
                    AND sp.wave_id IS NULL
                    AND (
                        (sp.state IN ('partially_available', 'assigned')
                        AND sp.move_type <> 'one')
                        OR
                        (sp.state = 'assigned' AND sp.move_type = 'one')
                        )
                    AND sp.picking_type_id IN %(picking_type_ids)s
                    AND ri.state IN ('draft', 'pending', 'close')
                    AND EXISTS (
                        SELECT 1 FROM stock_pack_operation spo
                            JOIN stock_location sl ON spo.location_id = sl.id
                            WHERE spo.picking_id = sp.id
                                AND sl.is_valid_location
                                )
                    AND (
                        (
                        sp.operator_id IS NULL
                        AND sp.printed = false
                        AND ri.picking_launched
                        AND (
                            NOT EXISTS (SELECT 1
                                    FROM res_users_round_instance_rel
                                    WHERE round_instance_id=ri.id
                                        )
                            OR EXISTS (SELECT 1
                                    FROM res_users_round_instance_rel
                                    WHERE round_instance_id = ri.id
                                    AND res_users_id = %(operator)s
                                    )
                            )
                        )
                        OR
                        (
                            sp.operator_id = %(operator)s
                            AND sp.state NOT IN ('done', 'cancel')
                        )
                        )
                    ORDER BY ri.date, ri.time_picking_planned
        """
        params = {
            "operator": user.id,
            "picking_type_ids": tuple(domain["picking_type_id"]),
        }
        self.env.cr.execute(query, params)
        result = self.env.cr.fetchall()
        ids = []
        for row in result:
            if not row[1] in ids:
                ids.append(row[1])
        delivery_rounds = self.env["round.instance"].browse(ids)
        return delivery_rounds

    def _get_delivery_round_id(self, domain, operator):
        """
        We want to get the first delivery_round with need to process
        for the selected operator asking for a batch picking
        """
        delivery_rounds = self._get_delivery_rounds_candidates(domain, operator)
        if not delivery_rounds:
            msg = "No delivery rounds to prepare for the picking type you chose"
            raise ValidationError(_(msg))
        delivery_rounds_authorized = delivery_rounds.filtered(
            lambda d: operator in d.operator_ids if d.operator_ids else True
        )
        if not delivery_rounds_authorized:
            msg = (
                "Operator %s is not into any list of operators allowed for preparing delivery rounds"
                % operator.name
            )
            raise ValidationError(_(msg))
        delivery_round = delivery_rounds_authorized[0]
        return delivery_round.id

    def _search_pickings_domain(self, user=None):
        domain = super(MakePickingBatch, self)._search_pickings_domain(user=user)
        domain_dict = {d[0]: d[2] for d in domain}
        operator = self.user_id if self.user_id else self.env.user
        delivery_round_id = self._get_delivery_round_id(domain_dict, operator)
        if delivery_round_id and operator and operator.cluster_by_delivery_round:
            domain.append(("delivery_round_id", "=", delivery_round_id))
        return domain

    def _candidates_pickings_to_batch(self, user=None):
        candidates_pickings = super(
            MakePickingBatch, self
        )._candidates_pickings_to_batch(user=user)
        if not user.cluster_by_delivery_round:
            # order pickings by delivery round before processing them
            query = """
            SELECT sp.id FROM stock_picking sp
                JOIN round_instance ri ON sp.delivery_round_id = ri.id
                WHERE sp.id  in %(picking_ids)s
                    ORDER BY sp.operator_id,
                            %(order_by)s
                            ri.date,
                            ri.time_picking_planned,
                            ri.id ASC
            """
            params = {
                "picking_ids": tuple(candidates_pickings.ids),
                "order_by": AsIs(
                    self._rounds_to_orderby_query(
                        self._operator_assigned_instances(user)
                    )
                ),
            }

            self.env.cr.execute(query, params)
            result = self.env.cr.fetchall()
            ids = []
            for row in result:
                if not row[0] in ids:
                    ids.append(row[0])
            candidates_pickings = self.env["stock.picking"].browse(ids)
        return candidates_pickings

    @api.model
    def _operator_assigned_instances(self, operator_id=None):
        operator_id = operator_id or self.env.user
        domain_rounds = [("state", "in", ["pending", "open", "close"])]
        open_rounds = self.env["round.instance"].search(domain_rounds)
        return open_rounds.filtered(lambda r: operator_id in r.operator_ids)

    @api.model
    def _rounds_to_orderby_query(self, round_instances):
        order_clause = ""
        if round_instances:
            cases = ["WHEN %s THEN 0" % i for i in round_instances.ids]
            order_clause = "CASE ri.id %s ELSE 1 END, " % " ".join(cases)
        return order_clause
