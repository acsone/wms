# -*- coding: utf-8 -*-
# Copyright 2017 Sylvain Van Hoof (Okia SPRL)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ProductProduct(models.Model):
    _inherit = 'product.product'

    product_additional_id = fields.Many2one('product.template',
                                            string='Additional product',
                                            compute='_compute_product_add',
                                            store=True,
                                            readonly=True)

    @api.depends('product_tmpl_id.bom_ids',
                 'product_tmpl_id.bom_ids.product_tmpl_id')
    def _compute_product_add(self):
        for product in self:
            kits = product.product_tmpl_id.bom_ids\
                .filtered(lambda bom: bom.bom_with_additional_product)

            if not kits:
                product.product_additional_id = None
                continue

            # There is check on BOM who validate that the structure of all
            # BOM for a product is the same. It means that we can take
            # the first BOM.
            bom_additional_product = kits[0].bom_line_ids\
                .filtered(lambda line: line.is_additional_product)
            if not bom_additional_product:
                raise UserError(_('There is not additional product for '
                                  'this BOM. Please contact your manager. '
                                  '(BOM %s (%s)') % (product.name,
                                                     product.id))
            elif len(bom_additional_product) > 1:
                raise UserError(_('There are more than one additional product'
                                  ' on this BOM. Please contact your manager.'
                                  ' (BOM %s (%s)') % (product.name,
                                                      product.id))

            additional_product = bom_additional_product.product_id
            product.product_additional_id = additional_product.id
