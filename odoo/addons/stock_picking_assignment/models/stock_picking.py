# -*- coding: utf-8 -*-
# © 2016 Sylvain Van Hoof (Okia sprl) <sylvain@okia.be>
# © 2016-2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    # Odoo Fix: never copy the printed field. Important for backorder creation
    printed = fields.Boolean(copy=False, track_visibility="onchange")

    operator_id = fields.Many2one(
        "res.users", string="Operator", copy=False, track_visibility="onchange"
    )
    can_assign_operator = fields.Boolean(
        string="Ready for Operator", compute="_compute_can_assign_operator",
    )

    def _prepare_assign_operator_values(self):
        return {"operator_id": self.env.uid, "printed": True}

    @api.multi
    def assign_operator(self):
        self.write(self._prepare_assign_operator_values())

    @api.depends("state", "operator_id", "is_blocked_by_picking_policy")
    def _compute_can_assign_operator(self):
        for record in self:
            to_process = record.state in ["assigned", "partially_available"]
            record.can_assign_operator = (
                to_process
                and not record.operator_id
                and not record.is_blocked_by_picking_policy
            )
