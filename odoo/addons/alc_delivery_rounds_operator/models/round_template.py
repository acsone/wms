# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class RoundTemplate(models.Model):

    _inherit = "round.template"

    operator_ids = fields.Many2many(
        "res.users",
        string="Operators",
        copy=False,
        help="Operators assigned to this delivery. Fill this list to restrict the "
        "processing of the pickings to specific list of operators. Leaves"
        "empty to allows the processing by any operator.",
    )
