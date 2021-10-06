# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, models
from odoo.exceptions import ValidationError


class MakePickingBatch(models.TransientModel):

    _inherit = "make.picking.batch"

    def _get_delivery_rounds_candidates(self, domain, user):
        query = """
            SELECT sp.id, ri.id FROM stock_picking sp
                JOIN stock_picking_type spt ON sp.picking_type_id = spt.id
                JOIN round_instance ri ON sp.delivery_round_id = ri.id
                WHERE sp.picking_type_subcode = 'PICK'
                    AND sp.wave_id IS NULL
                    AND (
                        (sp.state IN ('partially_available', 'assigned')
                        AND sp.move_type <> 'one')
                        OR
                        (sp.state = 'assigned' AND sp.move_type = 'one')
                        )
                    AND spt.id IN %(picking_type_ids)s
                    AND ri.state IN ('draft', 'pending', 'close')
                    AND EXISTS (
                        SELECT 1 FROM stock_pack_operation spo
                            JOIN stock_location sl ON spo.location_id = sl.id
                            WHERE spo.picking_id = sp.id
                                AND sl.is_valid_location
                                )
                    AND (
                        (
                        sp.user_id IS NULL
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
                            sp.user_id = %(operator)s
                            AND sp.state NOT IN ('done', 'cancel')
                        )
                        )
                    ORDER BY ri.date, ri.time_leave_planned
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

    def _get_delivery_round_id(self, domain):
        """
        We want to get the first delivery_round with need to process
        for the selected operator asking for a batch picking
        """
        user = self.user_id if self.user_id else self.env.user
        delivery_rounds = self._get_delivery_rounds_candidates(domain, user)
        if not delivery_rounds:
            msg = "No delivery rounds to prepare for the picking type you chose"
            raise ValidationError(_(msg))
        delivery_rounds_authorized = delivery_rounds.filtered(
            lambda d: user in d.operator_ids if d.operator_ids else True
        )
        if not delivery_rounds_authorized:
            msg = (
                "Operator %s is not into any list of operators allowed for preparing delivery rounds"
                % user.name
            )
            raise ValidationError(_(msg))
        delivery_round = delivery_rounds_authorized[0]
        return delivery_round.id

    def _search_pickings_domain(self, user=None):
        domain = super(MakePickingBatch, self)._search_pickings_domain(user=user)
        domain_dict = {d[0]: d[2] for d in domain}
        delivery_round_id = self._get_delivery_round_id(domain_dict)
        if delivery_round_id:
            domain.append(("delivery_round_id", "=", delivery_round_id))
        return domain
