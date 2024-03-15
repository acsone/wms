# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_compare

from odoo.addons.stock.models.stock_picking import Picking as PickingBase


class StockPicking(PickingBase):

    can_put_in_pack = fields.Boolean(compute="_compute_can_put_in_pack")
    can_unreserve_moves = fields.Boolean(
        compute="_compute_can_unreserve_moves", default=True
    )
    quant_reserved_exist = fields.Boolean(compute="_compute_quant_reserved_exist")
    is_put_in_pack_done = fields.Boolean("Put in Pack done", default=False)

    @api.depends("gls_package_ref")
    def _compute_can_unreserve_moves(self):
        for rec in self:
            rec.can_unreserve_moves = not bool(rec.gls_package_ref)

    def _compute_quant_reserved_exist(self):
        for picking in self:
            picking.quant_reserved_exist = any(
                picking.move_line_ids.mapped("reserved_uom_qty")
            )

    def _filter_can_put_in_pack(self, move_line):
        qty = move_line.qty_done
        precision = move_line.product_uom_id.rounding
        return (
            float_compare(qty, 0.0, precision_rounding=precision) > 0
            and move_line.result_package_id.package_type_id.package_carrier_type
            != "gls"
        )

    @api.depends(
        "move_line_ids",
        "move_line_ids.qty_done",
        "move_line_ids.result_package_id",
    )
    def _compute_can_put_in_pack(self):
        for record in self:
            lines = record.move_line_ids
            record.can_put_in_pack = bool(lines.filtered(self._filter_can_put_in_pack))

    def _get_gls_pack_package(self, operations):
        """Private method, only call it if conditions are checked before."""
        pack_operation_candidates = self.move_line_ids.browse()
        for op in (o for o in operations if not o.result_package_id):
            pack_operation_candidates |= op
        package = pack_operation_candidates.mapped("package_id")
        if len(package) > 1:
            raise ValidationError(_("More than one pack"))
        return package

    def _get_gls_put_in_pack_wizard_action(self, package_id):
        xmlid = "alc_gls_putinpack.delivery_package_gls_wizard_act_window"
        window_action = self.env["ir.actions.act_window"]._for_xml_id(xmlid)
        context = dict(
            self.env.context, default_picking_id=self.id, default_package_id=package_id
        )
        window_action["context"] = context
        return window_action

    def _pre_put_in_pack_hook(self, move_line_ids):
        """Override the standard hook called at put in pack action."""
        if (
            self.delivery_type == "gls"
            and self.picking_type_id.show_gls_put_in_pack_wizard
        ):
            return self._get_gls_put_in_pack_wizard_action(False)
        return super()._pre_put_in_pack_hook(move_line_ids)

    def button_validate(self):
        """If the packaging is missing on some package of a GLS picking, sending it.

        would fail anyway (on missing packaging). This means the user would have to
        open the wizard on the correct package.
        To simplify this process, we directly return the first missing one,
        so that clicking the button repeatedly would eventually work.
        """
        gls_pickings = self.filtered(lambda p: p.delivery_type == "gls")
        gls_packages = gls_pickings.mapped("package_ids")
        for package in gls_packages:
            if not package.package_type_id:
                return self._get_gls_put_in_pack_wizard_action(package.id)
        return super().button_validate()

    def do_unreserve(self):
        for rec in self:
            if not rec.can_unreserve_moves:
                raise ValidationError(
                    _("Moves cannot be unreserved because a GLS package already exist.")
                )
        return super().do_unreserve()
