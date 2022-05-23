# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductTemplate(models.Model):

    _inherit = "product.template"

    veterinary_group_ids = fields.Many2many(
        "veterinary.group",
        "product_template_veterinary_group_rel",
        "product_template_id",
        "veterinary_group_id",
        string="Veterinary Groups",
    )
