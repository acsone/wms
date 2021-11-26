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

    @api.depends("barcode", "no_barcode_authorized", "is_new")
    def _compute_missing_barcode(self):
        for product in self:
            product.missing_barcode = product.is_new and (
                not product.barcode and not product.no_barcode_authorized
            )

    @api.constrains("barcode", "no_barcode_authorized")
    def _check_barcode_is_mandatory(self):
        if not self.env.context.get("disable_check_barcode_constrains"):
            for product in self:
                if (
                    product.active
                    and not product.is_new
                    and not product.no_barcode_authorized
                    and not product.barcode
                ):
                    msg = _(
                        "You must enter a barcode or specify product without barcode"
                    )
                    raise ValidationError(msg)

    def write(self, vals):
        result = super(ProductProduct, self).write(vals)
        for rec in self:
            rec._check_barcode_is_mandatory()
        return result
