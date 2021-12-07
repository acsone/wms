# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

from ..exceptions import MissingBarcodeError, MissingDimensionsError, MissingWeightError


class StockPackOperationLotAdd(models.TransientModel):

    _inherit = "stock.pack.operation.lot.add"

    product_weight = fields.Float(
        string="Product weight",
        compute="_compute_product_weight",
        inverse="_inverse_product_weight",
    )
    product_length = fields.Float(
        string="Product length (cm)",
        compute="_compute_product_length",
        inverse="_inverse_product_length",
    )
    product_height = fields.Float(
        string="Product height (cm)",
        compute="_compute_product_height",
        inverse="_inverse_product_height",
    )
    product_width = fields.Float(
        string="Product width (cm)",
        compute="_compute_product_width",
        inverse="_inverse_product_width",
    )
    product_barcode = fields.Char(
        string="Barcode",
        compute="_compute_product_barcode",
        inverse="_inverse_product_barcode",
    )
    no_barcode_authorized = fields.Boolean(
        default=False,
        compute="_compute_no_barcode_authorized",
        inverse="_inverse_no_barcode_authorized",
    )

    product_is_new = fields.Boolean(related="product_id.is_new")
    product_packaging_ids = fields.One2many(
        "product.packaging", "Logistical Units", related="product_id.packaging_ids",
    )

    @api.depends("product_id", "product_id.is_new", "product_id.weight")
    def _compute_product_weight(self):
        for rec in self:
            product = rec.product_id
            if product.is_new:
                rec.product_weight = product.weight

    def _inverse_product_weight(self):
        for rec in self:
            product = rec.product_id
            if product.is_new:
                product.weight = rec.product_weight

    @api.depends("product_id", "product_id.is_new", "product_id.length")
    def _compute_product_length(self):
        for rec in self:
            product = rec.product_id
            if product.is_new:
                rec.product_length = product.length

    def _inverse_product_length(self):
        for rec in self:
            product = rec.product_id
            if product.is_new:
                product.length = rec.product_length

    @api.depends("product_id", "product_id.is_new", "product_id.height")
    def _compute_product_height(self):
        for rec in self:
            product = rec.product_id
            if product.is_new:
                rec.product_height = product.height

    def _inverse_product_height(self):
        for rec in self:
            product = rec.product_id
            if product.is_new:
                product.height = rec.product_height

    @api.depends("product_id", "product_id.is_new", "product_id.width")
    def _compute_product_width(self):
        for rec in self:
            product = rec.product_id
            if product.is_new:
                rec.product_width = product.width

    def _inverse_product_width(self):
        for rec in self:
            product = rec.product_id
            if product.is_new:
                product.width = rec.product_width

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

    def _check_barcode_new_product(self):
        for rec in self:
            if (
                rec.product_id.is_new
                and not rec.product_barcode
                and not rec.no_barcode_authorized
            ):
                raise MissingBarcodeError()

    def _check_dimensions_new_product(self):
        for rec in self:
            if rec.product_id.is_new and not (
                rec.product_width or rec.product_length or rec.product_height
            ):
                raise MissingDimensionsError()

    def _check_weight_new_product(self):
        for rec in self:
            if rec.product_id.is_new and not rec.product_weight:
                raise MissingWeightError()

    def _add(self):
        result = super(StockPackOperationLotAdd, self)._add()

        vals = {}
        product = self.product_id
        if self.product_is_new and self.product_packaging_ids:
            vals.update({"packaging_ids": [(6, 0, self.product_packaging_ids.ids)]})

        if vals:
            product.write(vals)

        # Manually check constrains because they depends on product_id.is_new which is
        # a computed field without an inverse. This raises a warning that triggers error.
        # For this reason, we check the constrains exactly when we need it : when receiving
        # the product.
        self._check_barcode_new_product()
        self._check_dimensions_new_product()
        self._check_weight_new_product()

        return result
