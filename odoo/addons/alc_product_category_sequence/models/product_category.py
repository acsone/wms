# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductCategory(models.Model):

    _inherit = "product.category"
    _parent_order = "sequence, name"
    _order = "sequence, parent_left"

    sequence = fields.Integer(required=False)
