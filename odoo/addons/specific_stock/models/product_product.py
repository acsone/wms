# -*- coding: utf-8 -*-
# Copyright 2016 Julien Coux (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    date_last_inventory = fields.Datetime("Last inventory", readonly=True)

    lot_ids = fields.One2many(domain=[("is_archived", "=", False)])
