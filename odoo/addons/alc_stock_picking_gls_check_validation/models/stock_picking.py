# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import SUPERUSER_ID, _, api, fields
from odoo.exceptions import UserError

from odoo.addons.alc_gls_putinpack.models import stock_picking


class StockPicking(stock_picking.StockPicking):

    gls_pack_in_picking = fields.Boolean(
        compute="_compute_gls_pack_in_picking",
        help="Technical field to check if there are packs in the current picking "
        "meaning they have to be processed first",
    )
    validate_allowed = fields.Boolean(compute="_compute_is_validate_allowed")

    @api.depends(
        "picking_type_code",
        "delivery_type",
        "has_packages",
        "package_level_ids.is_done",
    )
    def _compute_gls_pack_in_picking(self):
        for rec in self:
            rec.gls_pack_in_picking = (
                rec.picking_type_code == "outgoing"
                and rec.delivery_type == "gls"
                and (
                    rec.has_packages
                    and not all(package.is_done for package in rec.package_level_ids)
                )
            )

    @api.depends(
        "gls_pack_in_picking",
        "move_line_ids",
        "move_line_ids.qty_done",
        "move_line_ids.result_package_id",
    )
    def _compute_is_validate_allowed(self):
        for rec in self:
            if rec.picking_type_code == "outgoing" and rec.delivery_type == "gls":
                rec.validate_allowed = all(
                    rec.move_line_ids.mapped("qty_done")
                ) and all(o.result_package_id for o in rec.move_line_ids)
            else:
                rec.validate_allowed = True

    def _check_is_action_force_validate_allowed(self):
        has_group = (
            self.user_has_groups("base.group_no_one")
            or self.env.user.id == SUPERUSER_ID
        )
        allowed_states = ("draft", "partially_available", "assigned")
        states = self.mapped("state")
        if not has_group and any(s not in allowed_states for s in states):
            raise UserError(_("You are not allowed to force the validation"))

    def action_force_validate(self):
        self.ensure_one()
        self._check_is_action_force_validate_allowed()
        return self.with_context(bypass_check_validate_allowed=True).button_validate()

    def button_validate(self):
        if not self.env.context.get("bypass_check_validate_allowed"):
            validate_not_allowed_pickings = self.filtered(
                lambda p: not p.validate_allowed
            )
            if validate_not_allowed_pickings:
                raise UserError(
                    _(
                        "You cannot validate the picking before all the packs are done (%(picking_names)s)",
                        picking_names=", ".join(
                            validate_not_allowed_pickings.mapped("name")
                        ),
                    )
                )
        return super().button_validate()
