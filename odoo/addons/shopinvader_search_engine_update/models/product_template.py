# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class ProductTemplate(models.Model):

    _inherit = "product.template"

    def write(self, vals):
        res = super(ProductTemplate, self).write(vals)
        self.shopinvader_mark_to_update()
        return res

    def shopinvader_mark_to_update(self):
        self.sudo().mapped("product_variant_ids").shopinvader_mark_to_update()
