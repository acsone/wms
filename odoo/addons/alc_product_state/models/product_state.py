# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductState(models.Model):
    _name = "product.state"
    _order = "sequence"

    name = fields.Char(required=True, translate=True)
    code = fields.Char(required=True)
    sequence = fields.Integer()
