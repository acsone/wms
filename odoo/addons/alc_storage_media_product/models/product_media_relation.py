# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductMediaRelation(models.Model):
    _inherit = "product.media.relation"

    lang = fields.Selection(related="media_id.lang", readonly=False)
    media_type_id = fields.Many2one(readonly=False)
