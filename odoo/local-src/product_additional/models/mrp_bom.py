# -*- coding: utf-8 -*-
# Copyright 2017 Julien Coux (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    bom_with_additional_product = fields.Boolean(
        string='Bill of material with additional product',
    )

    @api.one
    @api.constrains('type', 'bom_with_additional_product', 'bom_line_ids')
    def _check_additional_product(self):
        if self.bom_with_additional_product:
            is_ok = (
                self.type == 'phantom' and
                len(self.bom_line_ids) == 2 and
                self.bom_line_ids.mapped('is_additional_product') in [
                    [False, True],
                    [True, False]
                ]
            )
            if not is_ok:
                raise ValidationError(_(
                    'A bill of material '
                    'with additional product must have \'kit\' type and '
                    '2 components of which only one is an additional product.'
                ))
        else:
            is_ok = (
                True not in self.bom_line_ids.mapped(
                    'is_additional_product'
                )
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
