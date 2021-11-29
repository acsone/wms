# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

from ..exceptions import MissingBarcodeError, MissingDimensionsError, MissingWeightError


class StockPackOperationLotAdd(models.TransientModel):

    _inherit = "stock.pack.operation.lot.add"

    display_product_dimensions = fields.Boolean(
        compute="_compute_display_missing_dimensions"
    )
    display_product_weight = fields.Boolean(compute="_compute_display_missing_weight")

    product_weight = fields.Float(string="Product weight")
    product_length = fields.Float(string="Product length (cm)")
    product_height = fields.Float(string="Product height (cm)")
    product_width = fields.Float(string="Product width (cm)")
    product_barcode = fields.Char(
        string="Barcode",
        oldname="ean13",
        compute="_compute_product_barcode",
        inverse="_inverse_product_barcode",
    )
    no_barcode_authorized = fields.Boolean(
        default=False,
        compute="_compute_no_barcode_authorized",
        inverse="_inverse_no_barcode_authorized",
    )
    product_is_new = fields.Boolean(related="product_id.is_new")

    @api.depends("product_id", "product_id.is_new", "product_id.has_no_dimensions")
    def _compute_display_missing_dimensions(self):
        for rec in self:
            product = rec.product_id
            rec.display_product_dimensions = (
                product.is_new and product.has_no_dimensions
            )

    @api.depends("product_id", "product_id.is_new", "product_id.missing_weight")
    def _compute_display_missing_weight(self):
        for rec in self:
            product = rec.product_id
            rec.display_product_weight = product.is_new and product.missing_weight

    @api.depends("product_id", "product_id.is_new", "product_id.barcode")
    def _compute_product_barcode(self):
        for rec in self:
            product = rec.product_id
            if product.is_new:
                rec.product_barcode = product.barcode

    def _inverse_product_barcode(self):
        for rec in self:
            product = rec.product_id
            if product.is_new:
                product.barcode = rec.product_barcode

    @api.depends("product_id", "product_id.is_new", "product_id.no_barcode_authorized")
    def _compute_no_barcode_authorized(self):
        for rec in self:
            product = rec.product_id
            if product.is_new:
                rec.no_barcode_authorized = product.no_barcode_authorized

    def _inverse_no_barcode_authorized(self):
        for rec in self:
            product = rec.product_id
            if product.is_new:
                product.no_barcode_authorized = rec.no_barcode_authorized

    def _add(self):
        res = super(StockPackOperationLotAdd, self)._add()
        no_barcode_and_barcode_must_be_defined = (
            self.product_is_new
            and not self.product_barcode
            and not self.no_barcode_authorized
        )

        missing_dimension = self.display_product_dimensions and not (
            self.product_width or self.product_length or self.product_height
        )
        missing_weight = self.display_product_weight and not self.product_weight

        if missing_weight:
            raise MissingWeightError()

        if missing_dimension:
            raise MissingDimensionsError()

        if no_barcode_and_barcode_must_be_defined:
            raise MissingBarcodeError()

        vals = {}
        product = self.product_id
        if self.display_product_dimensions:
            vals.update(
                {
                    "width": self.product_width,
                    "length": self.product_length,
                    "height": self.product_height,
                }
            )
        if self.display_product_weight:
            vals.update({"weight": self.product_weight})

        if self.product_is_new and (
            self.product_barcode != product.barcode
            or self.no_barcode_authorized != product.no_barcode_authorized
        ):
            vals.update(
                {
                    "barcode": self.product_barcode,
                    "no_barcode_authorized": self.no_barcode_authorized,
                }
            )
        if vals:
            product.write(vals)

        return res
