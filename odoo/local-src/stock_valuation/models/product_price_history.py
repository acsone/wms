# -*- coding: utf-8 -*-
# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


from odoo import fields, models


class ProductPriceHistory(models.Model):
    _inherit = 'product.price.history'
    _order = 'datetime desc, id desc'

    # override to add an index
    product_id = fields.Many2one(index=True)
