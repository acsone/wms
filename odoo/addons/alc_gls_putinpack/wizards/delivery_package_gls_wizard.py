# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import threading

from odoo import _, api, fields, models, registry
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_is_zero

from odoo.addons.stock.models.stock_package_type import PackageType
from odoo.addons.stock.models.stock_picking import Picking
from odoo.addons.stock.models.stock_quant import QuantPackage


class DeliveryPackageGlsWizard(models.TransientModel):
    _name = "delivery.package.gls.wizard"
    _description = "Wizard to prepare the package and send it to GLS."

    picking_id = fields.Many2one[Picking](
        string="Picking",
        required=True,
        domain=[("delivery_type", "=", "gls")],
    )
    allowed_package_ids = fields.Many2many[QuantPackage](
        string="Allowed Packages",
        compute="_compute_allowed_package_ids",
    )
    package_id = fields.Many2one[QuantPackage](
        string="Package",
        help="The package to send to GLS.",
        # domain="[('id', 'in', allowed_package_ids)]",  # when migrating, use this
    )
    package_id_domain = fields.Binary(
        compute="_compute_package_id_domain",
        readonly=True,
    )
    is_sent = fields.Boolean(
        string="Is sent",
        help="Technical field to know if we need to force resend.",
        compute="_compute_is_sent",
    )
    package_type_id = fields.Many2one[PackageType](
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
            key_packages = "move_line_ids.result_package_id"
            record.allowed_package_ids = record.picking_id.mapped(key_packages)

    @api.depends("allowed_package_ids")
    def _compute_package_id_domain(self):
        for record in self:
            ids = record.allowed_package_ids.ids
            record.package_id_domain = [("id", "in", ids)]

    @api.depends("package_id")
    def _compute_is_sent(self):
        for record in self:
            record.is_sent = bool(record.package_id.parcel_tracking)

    @api.onchange("picking_id")
    def onchange_picking_id(self):
        for rec in self:
            if rec.picking_id and rec.package_id not in rec.allowed_package_ids:
                sent = rec.allowed_package_ids.filtered("parcel_tracking")
                unsent = rec.allowed_package_ids - sent
                rec.package_id = unsent[0] if unsent else sent[0] if sent else False

    @api.onchange("package_id")
    def onchange_package_id(self):
        for rec in self:
            packaging = rec.package_id.package_type_id
            if not packaging or packaging.package_carrier_type != "gls":
                xml_id = "delivery_carrier_label_gls.packaging_gls_parcel"
                packaging = self.env.ref(xml_id)
            rec._set_shipping_weight()
            rec.package_type_id = packaging

    def _set_shipping_weight(self):
        precision = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        for record in self:
            if record.package_id:
                self.shipping_weight = self.package_id.shipping_weight
            if not record.package_id or float_is_zero(
                self.shipping_weight, precision_digits=precision
            ):
                ops = self.picking_id.move_line_ids.filtered(
                    lambda o: o.qty_done > 0 and not o.result_package_id
                )
                package = self.picking_id._get_gls_pack_package(ops)
                weight_ops = sum(ops.mapped(lambda o: o.qty_done * o.product_id.weight))
                self.shipping_weight = package.shipping_weight + weight_ops

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        for wiz in res:
            if not wiz.shipping_weight:
                wiz._set_shipping_weight()
        return res

    def _validate_parameters(self, put_in_pack=False):
        required_keys = ["package_type_id", "shipping_weight"]
        if not put_in_pack:
            required_keys.append("package_id")
        for f in required_keys:
            if not self[f]:
                raise ValidationError(_("Missing parameter: %(field)s", field=f))

    def put_in_pack(self):
        self._validate_parameters(put_in_pack=True)
        move_line_ids = self.picking_id._package_move_lines()
        package = self.picking_id._put_in_pack(move_line_ids)
        if not package:
            raise ValidationError(_("No package to process."))
        package.package_type_id = self.package_type_id
        package.shipping_weight = self.shipping_weight
        self.package_id = package.id
        self.picking_id.is_put_in_pack_done = True
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
        self.package_id.sudo().gls_cancel_shipment()
        gls_package_refs = filter(
            None, self.mapped("allowed_package_ids.gls_package_ref")
        )
        self.picking_id.gls_package_ref = ",".join(gls_package_refs)
        trackings = filter(None, self.mapped("allowed_package_ids.parcel_tracking"))
        self.picking_id.carrier_tracking_ref = ",".join(trackings)

    def _set_package_done(self):
        """
        As in Odoo, the _put_in_pack() method will fill in the package related.

        move lines if qty_done == 0, we do the same for the concerned package
        """
        for level in self.picking_id.package_level_ids:
            if not level.is_done:
                level.is_done = True

    def _send(self, put_in_pack=False):
        # we want to keep the package information details in case sending fails
        # however the package does not already exist if we put_in_pack; in that case,
        # the package is also rollbacked, so we can't write the info on it
        vals = {
            "shipping_weight": self.shipping_weight,
            "package_type_id": self.package_type_id.id,
        }
        package_id = self.package_id
        self.package_id.write(vals)
        self._set_package_done()
        if not put_in_pack and not (
            getattr(threading.current_thread(), "testing", False)
            or self.env.registry.in_test_mode()
        ):  # rollback hooks explode at test cleanup
            package_id = self.package_id.id
            dbname = self.env.cr.dbname
            context = self.env.context
            uid = self.env.uid

            @self.env.cr.postrollback.add
            def after_rollback():
                db_registry = registry(dbname)
                with db_registry.cursor() as cr:
                    env = api.Environment(cr, uid, context)
                    package = env["stock.quant.package"].browse(package_id)
                    package.write(vals)

        return self.picking_id.gls_send_shipping_package(self.package_id.sudo())
