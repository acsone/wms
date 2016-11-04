# -*- coding: utf-8 -*-
# © 2016 Julien Coux (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    additional_product_ids = fields.One2many(
        comodel_name='product.template.additional',
        inverse_name='original_product_id',
        string='Additional products',
        copy=False
    )
