# -*- coding: utf-8 -*-
# © 2016 Sylvain Van Hoof (Okia sprl) <sylvain@okia.be>
# © 2016-2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    # Odoo Fix: never copy the printed field. Important for backorder creation
    printed = fields.Boolean(copy=False, track_visibility="onchange")

    operator_id = fields.Many2one(
        "res.users", string="Operator", copy=False, track_visibility="onchange"
    )

    _sql_constraints = [
        (
            "operator_id_unique",
            "EXCLUDE (operator_id WITH =) WHERE ((state is not 'done' or state is not 'cancel') and (operator_id <> '' or operator_id is not null))",
            _("This operator is already assigned to another ongoing picking"),
        )
    ]

    def _prepare_assign_operator_values(self):
        return {"operator_id": self.env.uid, "printed": True}

    @api.multi
    def assign_operator(self):
        self.write(self._prepare_assign_operator_values())
