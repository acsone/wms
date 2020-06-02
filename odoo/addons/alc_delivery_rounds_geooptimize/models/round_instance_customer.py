# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class RoundInstanceCustomer(models.Model):

    _inherit = "round.instance.customer"

    is_rank_computed = fields.Boolean(readonly=True)
