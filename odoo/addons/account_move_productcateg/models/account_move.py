# -*- coding: utf-8 -*-
# Copyright 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    categ_id = fields.Many2one(
        'product.category',
        'Product Category',
        domain="[('type','=','normal')]",
    )

    def create(self, vals):
        if vals.get('product_id') and 'categ_id' not in vals:
            product = self.env['product.product'].browse(vals['product_id'])
            vals['categ_id'] = product.categ_id.id
        return super(AccountMoveLine, self).create(vals)

    def write(self, vals):
        if 'product_id' in vals and 'categ_id' not in vals:
            if vals.get('product_id'):
                product = self.env['product.product'].browse(
                    vals['product_id']
                )
                vals['categ_id'] = product.categ_id.id
            else:
                vals['categ_id'] = False
        return super(AccountMoveLine, self).write(vals)
