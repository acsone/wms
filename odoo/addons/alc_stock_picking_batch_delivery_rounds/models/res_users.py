# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResUsers(models.Model):

    _inherit = "res.users"

    cluster_by_delivery_round = fields.Boolean(
        string="Create cluster pickings by delivery rounds for this operator",
        default=True,
    )
