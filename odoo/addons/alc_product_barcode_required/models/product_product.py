# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProductProduct(models.Model):

    _inherit = "product.product"

    no_barcode_authorized = fields.Boolean(
        default=False, help="Barcode not required for this product",
    )
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

    @api.constrains("active", "is_new", "barcode", "no_barcode_authorized")
    def _check_barcode_is_mandatory(self):
        if not self.env.context.get("disable_check_barcode_constrains"):
            filter_bad = lambda p: (
                p.active
                and not p.is_new
                and not p.no_barcode_authorized
                and not p.barcode
            )
            bad_products = self.filtered(filter_bad)
            if bad_products:
                msg = _(
                    "You must enter a barcode or specify product without barcode. "
                    "Affected products ids: %s"
                )
                raise ValidationError(msg % bad_products.ids)

    def write(self, vals):
        result = super(ProductProduct, self).write(vals)
        for rec in self:
            rec._check_barcode_is_mandatory()
        return result
