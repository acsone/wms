# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class RoundTemplate(models.Model):

    _inherit = "round.template"

    allow_cluster_picking = fields.Boolean(
        default=False,
        string="Allow cluster picking",
        help="Allow cluster picking for delivery rounds of this template",
    )
