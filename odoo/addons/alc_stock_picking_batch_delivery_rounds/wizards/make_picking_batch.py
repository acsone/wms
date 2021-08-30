# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, models
from odoo.exceptions import ValidationError
from odoo.osv import expression


class MakePickingBatch(models.TransientModel):

    _inherit = "make.picking.batch"

    def _get_delivery_rounds_candidates(self, domain):
        query = """
                SELECT count(sp.id), sp.delivery_round_id, ri.date, ri.time_leave_planned
                FROM stock_picking sp JOIN round_instance ri
                ON sp.delivery_round_id = ri.id
                JOIN round_template rt ON rt.id = ri.template_id
                WHERE sp.picking_type_id IN %(picking_type_ids)s
                    AND sp.wave_id IS NULL
                    AND sp.operator_id IS NULL
                    AND sp.state IN %(picking_states)s
                    AND ri.state=%(delivery_round_state)s
                    AND rt.allow_cluster_picking = true
                GROUP BY sp.delivery_round_id, ri.date, ri.time_leave_planned
                ORDER BY ri.date, ri.time_leave_planned, count(sp.id) DESC;
        """
        params = {
            "picking_type_ids": tuple(domain["picking_type_id"]),
            "picking_states": domain["state"],
            "delivery_round_state": "draft",
        }
        self.env.cr.execute(query, params)
        return self.env.cr.fetchall()

    def _get_delivery_round_id(self, domain):
        """
        We want to get the first delivery_round with need to process
        for the selected operator asking for a batch picking
        """
        user = self.user_id if self.user_id else self.env.user
        result = self._get_delivery_rounds_candidates(domain)
        ids = [row[1] for row in result]
        delivery_rounds = self.env["round.instance"].browse(ids)
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

    def _search_pickings_domain(self):
        domain = super(MakePickingBatch, self)._search_pickings_domain()
        domain_dict = {d[0]: d[2] for d in domain}
        delivery_round_id = self._get_delivery_round_id(domain_dict)
        if delivery_round_id:
            domain = expression.AND(
                [domain, [("delivery_round_id", "=", delivery_round_id)]]
            )
        return domain
