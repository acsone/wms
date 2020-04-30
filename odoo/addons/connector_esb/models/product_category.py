# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ProductCategory(models.Model):
    _inherit = 'product.category'

    esb_ref = fields.Char(string='Reference for ESB', copy=False)
    alcyon_product_type = fields.Char(
        string='Alcyon Product Type',
        compute='_compute_alcyon_product_type',
        store=True,
    )

    @api.depends('esb_ref', 'parent_id.alcyon_product_type')
    def _compute_alcyon_product_type(self):
        for record in self:
            category = record
            while not category.esb_ref and category.parent_id:
                category = category.parent_id
            record.alcyon_product_type = category.esb_ref
