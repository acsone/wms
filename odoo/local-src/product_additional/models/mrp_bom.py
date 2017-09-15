# -*- coding: utf-8 -*-
# Copyright 2017 Julien Coux (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    bom_with_additional_product = fields.Boolean(
        string='Bill of material with additional product',
    )

    @api.multi
    @api.constrains('type', 'bom_with_additional_product', 'bom_line_ids')
    def _check_additional_product(self):
        for bom in self:
            if bom.bom_with_additional_product:
                is_ok = (
                    bom.type == 'phantom' and
                    len(bom.bom_line_ids) == 2 and
                    bom.bom_line_ids.mapped('is_additional_product') in [
                        [False, True],
                        [True, False]
                    ]
                )
                if not is_ok:
                    raise ValidationError(_(
                        'A bill of material with additional product '
                        'must have \'kit\' type and 2 components of '
                        'which only one is an additional product.'
                    ))

                # All BOM for a product should have the same structure
                # E.G.: If the product A has 2 BOMs, these BOMs should have
                # the same main product and the same additional product
                main_product = bom\
                    .bom_line_ids\
                    .filtered(lambda line: not line.is_additional_product)\
                    .product_id
                add_product = bom\
                    .bom_line_ids\
                    .filtered(lambda line: line.is_additional_product)\
                    .product_id

                boms_with_same_product = self.search([
                    ('bom_with_additional_product', '=', True),
                    ('product_tmpl_id', '=', bom.product_tmpl_id.id),
                    ('id', '!=', bom.id)
                ])
                for bom_with_same_product in boms_with_same_product:
                    bom_main_product = bom_with_same_product\
                        .bom_line_ids\
                        .filtered(lambda l: not l.is_additional_product)\
                        .product_id
                    bom_add_product = bom_with_same_product\
                        .bom_line_ids\
                        .filtered(lambda l: l.is_additional_product)\
                        .product_id

                    if bom_main_product != main_product \
                            or bom_add_product != add_product:
                        raise UserError(_('All BOM for a product should have '
                                          'the same main product and the same'
                                          ' additional product'))
            else:
                is_ok = all(
                    not line.is_additional_product
                    for line in self.bom_line_ids
                )
                if not is_ok:
                    raise ValidationError(_(
                        'A bill of material without additional product '
                        'must only have non additional product components.'
                    ))


class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    is_additional_product = fields.Boolean(
        string='Is additional product',
    )
