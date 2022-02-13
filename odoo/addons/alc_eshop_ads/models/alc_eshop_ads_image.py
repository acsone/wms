# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AlcEshopAdsImage(models.Model):

    _name = "alc.eshop.ads.image"
    _inherit = "image.relation.abstract"

    display_time = fields.Integer(required=True, default=-1)
    ads_id = fields.Many2one("alc.eshop.ads", ondelete="cascade")
