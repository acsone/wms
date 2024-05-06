# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields
from odoo.exceptions import ValidationError

from odoo.addons.alc_stock_receive_lot.wizards.stock_pack_operation_lot_add import (
    StockPackOperationLotAdd as StockPackOperationLotAddBase,
)
from odoo.addons.product.models.product_packaging import (
    ProductPackaging as ProductPackagingBase,
)


class StockPackOperationLotAdd(StockPackOperationLotAddBase):

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
    product_packaging_ids = fields.One2many[ProductPackagingBase](
        string="Logistical Units",
        related="product_id.packaging_ids",
        readonly=False,
    )
    edit_dimensions_barcode_fields = fields.Boolean(
        default=False, compute="_compute_edit_dimensions_barcode_fields"
    )

    @api.depends(
        "product_id",
        "product_id.is_new",
        "product_id.is_human",
        "product_id.is_food",
        "product_id.is_meds",
        "product_id.is_equipment",
        "product_id.is_mto",
    )
    def _compute_edit_dimensions_barcode_fields(self):
        for rec in self:
            product = rec.product_id
            rec.edit_dimensions_barcode_fields = (
                product.is_new
                or product.is_human
                or product.is_food
                or product.is_meds
                or product.is_equipment
            ) and not product.is_mto

    @api.depends("product_id", "edit_dimensions_barcode_fields", "product_id.weight")
    def _compute_product_weight(self):
        for rec in self:
            product = rec.product_id
            if rec.edit_dimensions_barcode_fields:
                rec.product_weight = product.weight

    def _inverse_product_weight(self):
        for rec in self:
            product = rec.product_id
            if rec.edit_dimensions_barcode_fields:
                product.sudo().write({"weight": rec.product_weight})

    @api.depends(
        "product_id", "edit_dimensions_barcode_fields", "product_id.product_length"
    )
    def _compute_product_length(self):
        for rec in self:
            product = rec.product_id
            if rec.edit_dimensions_barcode_fields:
                rec.product_length = product.product_length

    def _inverse_product_length(self):
        for rec in self:
            product = rec.product_id
            if rec.edit_dimensions_barcode_fields:
                product.sudo().write({"product_length": rec.product_length})

    @api.depends(
        "product_id", "edit_dimensions_barcode_fields", "product_id.product_height"
    )
    def _compute_product_height(self):
        for rec in self:
            product = rec.product_id
            if rec.edit_dimensions_barcode_fields:
                rec.product_height = product.product_height

    def _inverse_product_height(self):
        for rec in self:
            product = rec.product_id
            if rec.edit_dimensions_barcode_fields:
                product.sudo().write({"product_height": rec.product_height})

    @api.depends(
        "product_id", "edit_dimensions_barcode_fields", "product_id.product_width"
    )
    def _compute_product_width(self):
        for rec in self:
            product = rec.product_id
            if rec.edit_dimensions_barcode_fields:
                rec.product_width = product.product_width

    def _inverse_product_width(self):
        for rec in self:
            product = rec.product_id
            if rec.edit_dimensions_barcode_fields:
                product.sudo().write({"product_width": rec.product_width})

    @api.depends("product_id", "edit_dimensions_barcode_fields", "product_id.barcode")
    def _compute_product_barcode(self):
        for rec in self:
            product = rec.product_id
            if rec.edit_dimensions_barcode_fields:
                rec.product_barcode = product.barcode

    def _inverse_product_barcode(self):
        for rec in self:
            product = rec.product_id
            if rec.edit_dimensions_barcode_fields:
                product.sudo().write({"barcode": rec.product_barcode})

    @api.depends(
        "product_id",
        "edit_dimensions_barcode_fields",
        "product_id.no_barcode_authorized",
    )
    def _compute_no_barcode_authorized(self):
        for rec in self:
            product = rec.product_id
            if rec.edit_dimensions_barcode_fields:
                rec.no_barcode_authorized = product.no_barcode_authorized

    def _inverse_no_barcode_authorized(self):
        for rec in self:
            product = rec.product_id
            if rec.edit_dimensions_barcode_fields:
                product.sudo().write(
                    {"no_barcode_authorized": rec.no_barcode_authorized}
                )

    def _check_barcode_new_product(self):
        if (
            not self.env["ir.config_parameter"]
            .sudo()
            .get_param("reception_wizard_constraints")
        ):
            return
        for rec in self:
            if (
                rec.edit_dimensions_barcode_fields
                and not rec.product_barcode
                and not rec.no_barcode_authorized
            ):
                raise ValidationError(
                    _(
                        "You must enter a barcode for the product to receive or allow "
                        "the reception without barcode"
                    )
                )

    def _check_dimensions_product(self):
        if (
            not self.env["ir.config_parameter"]
            .sudo()
            .get_param("reception_wizard_constraints")
        ):
            return
        for rec in self:
            if rec.edit_dimensions_barcode_fields and not (
                rec.product_width > 0
                or rec.product_length > 0
                or rec.product_height > 0
            ):
                raise ValidationError(
                    _("You must enter dimensions for the product to receive")
                )

    def _check_weight_product(self):
        if (
            not self.env["ir.config_parameter"]
            .sudo()
            .get_param("reception_wizard_constraints")
        ):
            return
        for rec in self:
            if rec.edit_dimensions_barcode_fields and not rec.product_weight > 0:
                raise ValidationError(
                    _("You must enter a weight for the product to receive")
                )

    def _add(self):
        result = super()._add()
        if (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("reception_wizard_constraints")
        ):
            # Manually check constraints because they depend on product_id.is_new which
            # is a computed field without an inverse. This raises a warning that
            # triggers the errors. For this reason, we check the constraints exactly
            # when we need to: when receiving the product.
            self._check_barcode_new_product()
            self._check_dimensions_product()
            self._check_weight_product()

        return result
