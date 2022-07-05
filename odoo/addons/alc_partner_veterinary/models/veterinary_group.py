# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class VeterinaryGroup(models.Model):

    _name = "veterinary.group"
    _description = "Veterinary Group"

    name = fields.Char(string="Name")
    partner_ids = fields.Many2many(
        "res.partner",
        "res_partner_veterinary_group_rel",
        "res_partner_id",
        "veterinary_group_id",
        string="Partners",
    )
    product_template_ids = fields.Many2many(
        "product.template",
        "product_template_veterinary_group_rel",
        "veterinary_group_id",
        "product_template_id",
        string="Products",
    )
