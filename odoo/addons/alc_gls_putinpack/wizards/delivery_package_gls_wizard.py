# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json
import threading

from odoo import _, api, fields, models, registry
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
        # domain="[('id', 'in', allowed_package_ids)]",  # when migrating, use this
    )
    package_id_domain = fields.Char(
        compute="_compute_package_id_domain", readonly=True, store=False,
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
    can_put_in_pack = fields.Boolean(
        related="picking_id.can_put_in_pack", readonly=True
    )

    @api.depends("picking_id")
    def _compute_allowed_package_ids(self):
        for record in self:
            key_packages = "pack_operation_product_ids.result_package_id"
            record.allowed_package_ids = record.picking_id.mapped(key_packages)

    @api.depends("allowed_package_ids")
    def _compute_package_id_domain(self):
        for record in self:
            ids = record.allowed_package_ids.ids
            record.package_id_domain = json.dumps([("id", "in", ids)])

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
        self._set_shipping_weight()
        self.packaging_id = packaging

    def _set_shipping_weight(self):
        for record in self:
            if record.package_id:
                self.shipping_weight = self.package_id.shipping_weight
            else:
                filter_ops = lambda o: o.qty_done > 0 and not o.result_package_id
                ops = self.picking_id.pack_operation_ids.filtered(filter_ops)
                package = self.picking_id._get_gls_pack_package(ops)
                weight_ops = sum(ops.mapped(lambda o: o.qty_done * o.product_id.weight))
                self.shipping_weight = package.shipping_weight + weight_ops

    @api.model
    def create(self, vals):
        res = super(DeliveryPackageGlsWizard, self).create(vals)
        res._set_shipping_weight()
        return res

    def _validate_parameters(self, put_in_pack=False):
        required_keys = ["packaging_id", "shipping_weight"]
        if not put_in_pack:
            required_keys.append("package_id")
        for f in required_keys:
            if not self[f]:
                raise ValidationError(_("Missing parameter: %s") % f)

    def put_in_pack(self):
        self._validate_parameters(put_in_pack=True)
        res = self.picking_id.put_in_pack()
        if not res:
            raise ValidationError(_("No package to process."))
        self.package_id = res["res_id"] if isinstance(res, dict) else res.id
        return self._send(put_in_pack=True)

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
        gls_package_refs = filter(
            None, self.mapped("allowed_package_ids.gls_package_ref")
        )
        self.picking_id.gls_package_ref = ",".join(gls_package_refs)
        trackings = filter(None, self.mapped("allowed_package_ids.parcel_tracking"))
        self.picking_id.carrier_tracking_ref = ",".join(trackings)

    def _send(self, put_in_pack=False):
        # we want to keep the package information details in case sending fails
        # however the package does not already exist if we put_in_pack; in that case,
        # the package is also rollbacked, so we can't write the info on it
        self.write_package_vals()
        if not put_in_pack and not (
            getattr(threading.currentThread(), "testing", False)
            or self.env.registry.in_test_mode()
        ):  # rollback hooks explode at test cleanup
            self.env.cr.after("rollback", lambda: self.write_package_vals(True))
        return self.picking_id.gls_send_shipping_package(self.package_id)

    def write_package_vals(self, after_rollback=False):
        vals_package = {
            "shipping_weight": self.shipping_weight,
            "packaging_id": self.packaging_id.id,
        }
        if after_rollback:
            with api.Environment.manage():
                with registry(self.env.cr.dbname).cursor() as new_cr:
                    new_env = api.Environment(new_cr, self.env.uid, self.env.context)
                    self.package_id.with_env(new_env).write(vals_package)
        else:
            self.package_id.write(vals_package)
