# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductProduct(models.Model):

    _inherit = "product.product"
    no_barcode_authorized = fields.Boolean(default=False)

    missing_weight = fields.Boolean(default=False, compute="_compute_missing_weight")
    missing_barcode = fields.Boolean(default=False, compute="_compute_missing_barcode")

    @api.depends("weight")
    def _compute_missing_weight(self):
        for product in self:
            product.missing_weight = not product.weight

    @api.depends(
        "barcode", "no_barcode_authorized", "product_tmpl_id", "product_tmpl_id.is_new"
    )
    def _compute_missing_barcode(self):
        for product in self:
            product.missing_barcode = product.product_tmpl_id.is_new and (
                not product.barcode and not product.no_barcode_authorized
            )
