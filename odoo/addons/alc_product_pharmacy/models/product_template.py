# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductTemplate(models.Model):

    _inherit = "product.template"

    code_cti = fields.Char("Code CTI Extended")
    code_amm = fields.Char("AMM Number")

    pharmacy_only = fields.Boolean("Only Pharmacies?")
