# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):

    _inherit = "res.partner"

    eshop_ordering_allowed = fields.Boolean(
        help="If not set, this partner is not allowed to pass an order on the eshop.",
        default=True,
    )
