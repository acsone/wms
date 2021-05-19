# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class RoundInstance(models.Model):

    _inherit = "round.instance"

    operator_ids = fields.Many2many(
        "res.users",
        string="Operators",
        copy=False,
        help="Operators assigned to this delivery. Fill this list to restrict the "
        "processing of the pickings to specific list of operators. Leaves"
        "empty to allows the processing by any operator.",
    )

    @api.model
    def create(self, vals):
        if "operator_ids" not in vals:
            template = self.env["round.template"].browse(vals["template_id"])
            if template.operator_ids:
                vals["operator_ids"] = [(6, 0, template.operator_ids.ids)]
        return super(RoundInstance, self).create(vals)
