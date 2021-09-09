# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import SUPERUSER_ID, _, api, fields, models
from odoo.exceptions import UserError


class StockPicking(models.Model):

    _inherit = "stock.picking"

    gls_pack_in_picking = fields.Boolean(
        compute="_compute_gls_pack_in_picking",
        help="Technical field to check if there are packs in the current picking meaning they have to be processed first",
    )
    validate_allowed = fields.Boolean(compute="_compute_is_validate_allowed")

    @api.depends("picking_type_code", "delivery_type", "pack_operation_pack_ids")
    def _compute_gls_pack_in_picking(self):
        for rec in self:
            rec.gls_pack_in_picking = (
                rec.picking_type_code == "outgoing"
                and rec.delivery_type == "gls"
                and rec.pack_operation_pack_ids
            )

    @api.depends(
        "gls_pack_in_picking",
        "pack_operation_ids",
        "pack_operation_ids.is_done",
        "pack_operation_ids.result_package_id",
    )
    def _compute_is_validate_allowed(self):
        for rec in self:
            if rec.picking_type_code == "outgoing" and rec.delivery_type == "gls":
                rec.validate_allowed = all(
                    rec.pack_operation_ids.mapped("is_done")
                ) and all(o.result_package_id for o in rec.pack_operation_ids)
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

    @api.multi
    def action_force_validate(self):
        self.ensure_one()
        self._check_is_action_force_validate_allowed()
        return self.with_context(bypass_check_validate_allowed=True).do_new_transfer()

    @api.multi
    def do_new_transfer(self):
        self.ensure_one()

        if (
            not self.env.context.get("bypass_check_validate_allowed")
            and not self.validate_allowed
        ):
            raise UserError(
                _("You cannot validate the picking before all the packs are done")
            )

        return super(StockPicking, self).do_new_transfer()
