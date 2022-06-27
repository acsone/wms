# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from psycopg2.extensions import AsIs

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class MakePickingBatch(models.TransientModel):

    _inherit = "make.picking.batch"
    only_one_delivery_round_by_cluster = fields.Boolean(
        string="Create cluster pickings by delivery rounds for this scenario",
        default=True,
    )

    def _get_delivery_rounds_candidates(self, picking_type_ids, user):
        query = """
            SELECT sp.id, ri.id FROM stock_picking sp
                JOIN round_instance ri ON sp.delivery_round_id = ri.id
                JOIN stock_picking_type spt ON sp.picking_type_id = spt.id
                JOIN picking_zone pz on pz.id = spt.picking_zone_id
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
                    AND sp.printed = false
                    AND (
                        (pz.code = '02' AND ri.picking_mat_launched)
                        OR
                        (pz.code = '03' AND ri.picking_frigo_launched)
                        OR
                        (pz.code = '04' AND ri.picking_ali_launched)
                        OR
                        (pz.code = '05' AND ri.picking_med_launched)
                    )
                    AND EXISTS (
                        SELECT 1 FROM stock_pack_operation spo
                            JOIN stock_location sl ON spo.location_id = sl.id
                            WHERE spo.picking_id = sp.id
                                AND sl.is_valid_location
                                )
                    AND (
                        (
                        sp.operator_id IS NULL
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
                    ORDER BY sp.operator_id,
                            %(order_by)s
                            ri.date,
                            ri.time_picking_planned,
                            ri.id ASC

        """
        params = {
            "operator": user.id,
            "picking_type_ids": tuple(picking_type_ids),
            "order_by": AsIs(
                self._rounds_to_orderby_query(self._operator_assigned_instances(user))
            ),
        }
        self.env.cr.execute(query, params)
        result = self.env.cr.fetchall()
        ids = []
        for row in result:
            if not row[1] in ids:
                ids.append(row[1])
        delivery_rounds = self.env["round.instance"].browse(ids)
        return delivery_rounds

    def _get_delivery_rounds(self, picking_type_ids, operator):
        """
        We want to get the first delivery_round with need to process
        for the selected operator asking for a batch picking
        """
        delivery_rounds = self._get_delivery_rounds_candidates(
            picking_type_ids, operator
        )
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
        return delivery_rounds_authorized

    def _search_pickings_domain(self, user=None):
        domain = super(MakePickingBatch, self)._search_pickings_domain(user=user)
        domain_dict = {d[0]: d[2] for d in domain}
        operator = self.user_id if self.user_id else self.env.user
        picking_type_ids = domain_dict["picking_type_id"]
        delivery_rounds_authorized = self._get_delivery_rounds(
            picking_type_ids, operator
        )
        if (
            delivery_rounds_authorized
            and (self.only_one_delivery_round_by_cluster)
            or (
                not self.only_one_delivery_round_by_cluster
                and operator.only_one_delivery_round_by_cluster
            )
        ):
            delivery_round = delivery_rounds_authorized[0]
            domain.append(("delivery_round_id", "=", delivery_round.id))
        return domain

    def _candidates_pickings_to_batch(self, user=None):
        candidates_pickings = super(
            MakePickingBatch, self
        )._candidates_pickings_to_batch(user=user)

        if (
            not self.only_one_delivery_round_by_cluster
            and not user.only_one_delivery_round_by_cluster
        ):
            # Filter out delivery round unauthorized:
            picking_type_ids = candidates_pickings.mapped("picking_type_id").ids
            delivery_rounds_authorized = self._get_delivery_rounds(
                picking_type_ids, user
            )
            candidates_pickings = candidates_pickings.filtered(
                lambda p: p.delivery_round_id in delivery_rounds_authorized
            ).sorted(
                key=lambda p, drs=delivery_rounds_authorized: drs.ids.index(
                    p.delivery_round_id.id
                )
            )

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
