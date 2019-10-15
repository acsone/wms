# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import odoo.addons.decimal_precision as dp
from odoo import _, api, fields, models


class ProductProduct(models.Model):
    _inherit = 'product.product'
    _order = 'default_code'


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    _order = 'default_code'

    medical_device = fields.Boolean(string='Medical Device')

    sale_price_2 = fields.Float(
        digits=dp.get_precision('Product Price'),
        compute='_compute_sale_price_2',
        readonly=True,
        store=False,
        string='Sale Price 2',
    )

    cnk_code = fields.Char(string='CNK', copy=False)

    indicated_price = fields.Float(string='Indicated price')

    storage_temperature_id = fields.Many2one(
        'product.storage.temperature', string="Storage temperature"
    )

    web_published = fields.Boolean(string="Published on website")

    veterinary_only = fields.Boolean(string='Veterinary only')
    belgium_only = fields.Boolean(string='Belgium only')

    _sql_constraints = [
        (
            'uniq_cnk_code',
            'unique(cnk_code)',
            _("This cnk_code already exists."),
        )
    ]

    def _compute_sale_price_2(self):
        for product in self:
            pricelist = self.env.ref('specific_data.product_pricelist_pb2')

            item_count = self.env['product.pricelist.item'].search_count(
                [
                    ('pricelist_id', '=', pricelist.id),
                    ('applied_on', '=', '1_product'),
                    ('product_tmpl_id', '=', product.id),
                ]
            )

            # We check if product price is modified by the price list
            if item_count and product.product_variant_ids:
                price = pricelist.price_get(
                    prod_id=product.product_variant_ids[0].id, qty=1
                )
                product.sale_price_2 = price.get(pricelist.id, 0.0)

    @api.model
    def create(self, vals):
        vals = ProductTemplate._remove_spaces_from_cnk(vals)
        return super(ProductTemplate, self).create(vals)

    @api.multi
    def write(self, vals):
        vals = ProductTemplate._remove_spaces_from_cnk(vals)
        return super(ProductTemplate, self).write(vals)

    @staticmethod
    def _remove_spaces_from_cnk(vals):
        if 'cnk_code' in vals and vals['cnk_code']:
            vals['cnk_code'] = vals['cnk_code'].replace(' ', '')
        return vals
