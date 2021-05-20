# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class RestLog(models.Model):

    _inherit = "rest.log"

    operator_id = fields.Many2one(
        "res.users", string="Operator", copy=False, index=True
    )
