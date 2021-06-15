# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class DeliveryPackageGlsWizard(models.TransientModel):
    _name = "delivery.package.gls.wizard"
    _description = "Wizard to prepare the package and send it to GLS."

    picking_id = fields.Many2one(
        comodel_name="stock.picking",
        string="Picking",
        required=True,
        domain=[("delivery_type", "=", "gls")],
    )
    allowed_package_ids = fields.Many2many(
        comodel_name="stock.quant.package",
        string="Package",
        compute="_compute_allowed_package_ids",
    )
    package_id = fields.Many2one(
        comodel_name="stock.quant.package",
        string="Package",
        help="The package to send to GLS.",
        domain="[('id', 'in', allowed_package_ids)]",
    )
    is_sent = fields.Boolean(
        string="Is sent",
        help="Technical field to know if we need to force resend.",
        compute="_compute_is_sent",
    )
    packaging_id = fields.Many2one(
        comodel_name="product.packaging",
        string="Packaging Type",
        domain=[("package_carrier_type", "=", "gls")],
    )
    shipping_weight = fields.Float(string="Shipping Weight")

    @api.depends("picking_id")
    def _compute_allowed_package_ids(self):
        for record in self:
            key_packages = "pack_operation_product_ids.result_package_id"
            record.allowed_package_ids = record.picking_id.mapped(key_packages)

    @api.depends("package_id")
    def _compute_is_sent(self):
        for record in self:
            record.is_sent = bool(record.package_id.parcel_tracking)

    @api.onchange("picking_id")
    def onchange_picking_id(self):
        if self.picking_id and self.package_id not in self.allowed_package_ids:
            sent = self.allowed_package_ids.filtered("parcel_tracking")
            unsent = self.allowed_package_ids - sent
            self.package_id = unsent[0] if unsent else sent[0] if sent else False

    @api.onchange("package_id")
    def onchange_package_id(self):
        if self.package_id.packaging_id:
            packaging = self.package_id.packaging_id
        else:
            xml_id = "delivery_carrier_label_gls.product_packaging_gls_parcel"
            packaging = self.env.ref(xml_id)
        self.shipping_weight = self.package_id.shipping_weight
        self.packaging_id = packaging

    def _validate_parameters(self):
        for f in ["package_id", "packaging_id", "shipping_weight"]:
            if not self[f]:
                raise ValidationError(_("Missing parameter: %s") % f)

    def resend(self):
        """Cancel the package and then resend it to GLS."""
        self._validate_parameters()
        self.abort()
        return self._send()

    def send(self):
        """Send the package to GLS."""
        self._validate_parameters()
        return self._send()

    def abort(self):
        self.package_id.gls_cancel_shipment()
        gls_package_refs = [s for s in self.allowed_package_ids.gls_package_ref if s]
        self.picking_id.gls_package_ref = ",".join(gls_package_refs)
        trackings = [s for s in self.allowed_package_ids.parcel_tracking if s]
        self.picking_id.carrier_tracking_ref = ",".join(trackings)

    def _send(self):
        self.package_id.shipping_weight = self.shipping_weight
        self.package_id.packaging_id = self.packaging_id
        return self.picking_id.gls_send_shipping_package(self.package_id)
