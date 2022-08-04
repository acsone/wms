# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class Country(models.Model):
    """Avoid creating country duplicates by forcing the code to be required."""

    _inherit = "res.country"

    code = fields.Char(required=True)
