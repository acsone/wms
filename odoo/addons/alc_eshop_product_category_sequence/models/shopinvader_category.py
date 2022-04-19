# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ShopinvaderCategory(models.Model):

    _inherit = "shopinvader.category"

    sequence = fields.Integer(related="record_id.sequence")
