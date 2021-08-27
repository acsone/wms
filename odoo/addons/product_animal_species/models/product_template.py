# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductTemplate(models.Model):

    _inherit = "product.template"

    species_id = fields.Many2one(string="Main Species", comodel_name="animal.species")
    species_ids = fields.Many2many(string="Species", comodel_name="animal.species")
