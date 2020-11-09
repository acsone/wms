# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AlcB2CBackend(models.Model):

    _inherit = "alc.b2c.backend"

    discount_pricelist_id = fields.Many2one(
        comodel_name="product.pricelist", string="Alcyon Discount"
    )
