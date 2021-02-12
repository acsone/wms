# -*- coding: utf-8 -*-
# Copyright 2016 Julien Coux (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    life_time = fields.Integer(related="categ_id.life_time")

    use_time = fields.Integer(related="categ_id.use_time")

    removal_time = fields.Integer(related="categ_id.removal_time")

    alert_time = fields.Integer(related="categ_id.alert_time")
