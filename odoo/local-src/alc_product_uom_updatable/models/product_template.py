# -*- coding: utf-8 -*-
# Copyright 2020 Acsone SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from itertools import groupby

from odoo import _, api, models
from odoo.exceptions import UserError


class ProductTemplate(models.Model):

    _inherit = 'product.template'

    @api.multi
    def write(self, vals):
        uom_id = False
        if 'uom_id' in vals:
            uom_id = vals.pop('uom_id')
        res = super(ProductTemplate, self).write(vals)
        if uom_id:
            self._update_uom(uom_id)
        return res

    @api.multi
    def _update_uom(self, uom_id):
        uom_obj = self.env["product.uom"]
        for key, products_group in groupby(self, key=lambda r: r.uom_id):
            product_list = list(products_group)
            product_id_list = []
            for product in product_list:
                product_id_list.append(product.id)
            old_uom_id = product_list[0].uom_id
            new_uom = uom_obj.search([("id", "=", uom_id)])
            if (
                old_uom_id.category_id == new_uom.category_id
                and old_uom_id.factor == new_uom.factor
            ):
                self.env.cr.execute(
                    'UPDATE product_template SET uom_id = %(uom)s WHERE id in %(product_id)s',
                    {'uom': new_uom.id, 'product_id': tuple(product_id_list)},
                )
            else:
                raise UserError(
                    _(
                        "You can not change the unit of measure of a product to a new unit that doesn't have the same category and factor"
                    )
                )
