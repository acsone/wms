# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class StockPackOperationLotAdd(models.TransientModel):

    _inherit = "stock.pack.operation.lot.add"

    missing_product_dimensions = fields.Boolean(
        default=False, compute="_compute_missing_product_dimensions"
    )
    missing_product_weight = fields.Boolean(
        default=False, compute="_compute_missing_product_weight"
    )
    missing_product_barcode = fields.Boolean(
        default=False, compute="_compute_missing_product_barcode"
    )
    no_barcode_authorized = fields.Boolean(default=False)
    product_weight = fields.Float(string="Product weight")
    product_length = fields.Float(string="Product length (cm)")
    product_height = fields.Float(string="Product height (cm)")
    product_width = fields.Float(string="Product width (cm)")
    product_barcode = fields.Char(string="Barcode", oldname="ean13")

    def _check_product_is_new(self, operation):
        storage_type_new = self.env.ref(
            "alc_stock_storage_type.package_st_M_M_Nouveaute", raise_if_not_found=False
        )
        product = operation.product_id
        is_new = (
            product.product_tmpl_id.product_package_storage_type_id.id
            == storage_type_new.id
        )
        return product, is_new

    @api.onchange("operation_id")
    def _compute_missing_product_dimensions(self):
        for rec in self:
            product, product_is_new = self._check_product_is_new(rec.operation_id)
            product_dimensions_missing = product and not (
                product.width or product.length or product.width
            )
            rec.missing_product_dimensions = bool(
                rec.operation_id and product_is_new and (product_dimensions_missing)
            )

    @api.onchange("operation_id")
    def _compute_missing_product_weight(self):
        for rec in self:
            product, product_is_new = self._check_product_is_new(rec.operation_id)
            rec.missing_product_weight = bool(
                rec.operation_id and product_is_new and not product.weight
            )

    @api.onchange("operation_id")
    def _compute_missing_product_barcode(self):
        for rec in self:
            product, product_is_new = self._check_product_is_new(rec.operation_id)
            rec.missing_product_barcode = bool(
                rec.operation_id and product_is_new and not product.barcode
            )

    def _add(self):
        res = super(StockPackOperationLotAdd, self)._add()
        no_barcode_and_barcode_must_be_defined = self.missing_product_barcode and not (
            self.product_barcode or self.no_barcode_authorized
        )
        missing_dimension = self.missing_product_dimensions and not (
            self.product_width or self.product_length or self.product_height
        )
        missing_weight = self.missing_product_weight and not self.product_weight
        if missing_dimension or missing_weight:
            raise UserError(
                _(
                    "Missing dimensions or weight. Please complete the info before making the reception."
                )
            )

        if no_barcode_and_barcode_must_be_defined:
            raise UserError(
                _(
                    "Missing barcode on the product you are trying to receive. If it is intentionnal, please check the 'no barcode for this product' box, else complete barcode."
                )
            )

        if (
            self.missing_product_dimensions
            or self.missing_product_weight
            or self.missing_product_barcode
        ):
            product = self.operation_id.product_id
            product.write(
                {
                    "width": self.product_width
                    if self.product_width
                    else product.width,
                    "length": self.product_length
                    if self.product_length
                    else product.length,
                    "height": self.product_height
                    if self.product_height
                    else product.height,
                    "weight": self.product_weight
                    if self.product_weight
                    else product.weight,
                    "barcode": self.product_barcode
                    if self.product_barcode
                    else product.barcode,
                    "no_barcode_authorized": self.no_barcode_authorized,
                }
            )
        return res
