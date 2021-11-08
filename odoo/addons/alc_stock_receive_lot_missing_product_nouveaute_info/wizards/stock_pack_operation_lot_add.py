# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

from ..exceptions import MissingBarcodeError, MissingDimensionsError, MissingWeightError


class StockPackOperationLotAdd(models.TransientModel):

    _inherit = "stock.pack.operation.lot.add"

    display_product_dimensions = fields.Boolean(
        compute="_compute_display_missing_infos"
    )
    display_product_weight = fields.Boolean(compute="_compute_display_missing_infos")
    display_product_barcode = fields.Boolean(compute="_compute_display_missing_infos")
    no_barcode_authorized = fields.Boolean(default=False)
    product_weight = fields.Float(string="Product weight")
    product_length = fields.Float(string="Product length (cm)")
    product_height = fields.Float(string="Product height (cm)")
    product_width = fields.Float(string="Product width (cm)")
    product_barcode = fields.Char(string="Barcode", oldname="ean13")

    @api.depends(
        "operation_id",
        "operation_id.product_id",
        "operation_id.product_id.is_new",
        "operation_id.product_id.has_no_dimensions",
        "operation_id.product_id.missing_barcode",
        "operation_id.product_id.missing_weight",
    )
    def _compute_display_missing_infos(self):
        for rec in self:
            product = rec.operation_id.product_id
            rec.display_product_barcode = product.missing_barcode
            rec.display_product_weight = (
                product.product_tmpl_id.is_new and product.missing_weight
            )
            rec.display_product_dimensions = (
                product.product_tmpl_id.is_new
                and product.product_tmpl_id.has_no_dimensions
            )

    def _add(self):
        res = super(StockPackOperationLotAdd, self)._add()
        no_barcode_and_barcode_must_be_defined = self.display_product_barcode and not (
            self.product_barcode or self.no_barcode_authorized
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

        product = self.operation_id.product_id

        vals = {}
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

        if self.display_product_barcode:
            vals.update(
                {
                    "barcode": self.product_barcode,
                    "no_barcode_authorized": self.no_barcode_authorized,
                }
            )
        if vals:
            product.write(vals)

        return res
