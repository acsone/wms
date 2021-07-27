# -*- coding: utf-8 -*-
# Copyright 2016 Julien Coux (Camptocamp)
# Copyright 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    is_action_force_transfer_allowed = fields.Boolean(
        compute="_compute_is_action_force_transfer_allowed"
    )

    is_create_backorder_allowed = fields.Boolean(
        compute="_compute_is_create_backorder_allowed"
    )

    @api.depends("state", "is_create_backorder_allowed")
    def _compute_is_action_force_transfer_allowed(self):
        allowed_states = ("draft", "partially_available", "assigned")
        for rec in self:
            rec.is_action_force_transfer_allowed = (
                rec.state in allowed_states or rec.is_create_backorder_allowed
            )

    @api.depends("pack_operation_ids.qty_done", "state", "move_lines.remaining_qty")
    def _compute_is_create_backorder_allowed(self):
        # check_backorder is not compute-safe, it drops the cache
        # so it has to be out of the loop
        to_check = self.filtered(
            lambda rec: rec.state == "draft"
            or all(x.qty_done == 0.0 for x in rec.pack_operation_ids)
        )
        checks = {rec: rec.check_backorder() for rec in to_check}
        for rec in self:
            # allow to transfer and create backorder even if no line processed
            rec.is_create_backorder_allowed = checks.get(rec, False)

    def _check_is_action_force_transfer_allowed(self):
        if any(not rec.is_action_force_transfer_allowed for rec in self):
            raise UserError(_("You are not allowed to force the transfer"))

    @api.multi
    def action_force_transfer(self):
        self._check_is_action_force_transfer_allowed()
        return self.do_new_transfer()

    @api.multi
    def do_new_transfer(self):
        self.ensure_one()

        if self.picking_type_code == "incoming":
            # At reception
            if (
                self.location_id.usage == "supplier"
                and self.check_backorder()
                and not self.env.context.get("__no_backorder_choice")
            ):
                # From a PO (not a return) and backorder to make
                return {
                    "type": "ir.actions.act_window",
                    "res_model": "stock.backorder.choice",
                    "views": [[False, "form"]],
                    "context": {"default_picking_id": self.id},
                    "target": "new",
                }
            return super(StockPicking, self).do_new_transfer()
        if self.check_backorder():
            # allow to process and create backorder even if no line
            # processed
            wiz = self.env["stock.backorder.confirmation"].create({"pick_id": self.id})
            wiz.process()
            return {}
        return super(StockPicking, self).do_new_transfer()

    @api.multi
    def do_transfer(self):
        to_backorder = self.filtered("is_create_backorder_allowed")
        to_transfer = self - to_backorder
        to_backorder._create_backorder()
        if to_transfer:
            return super(StockPicking, to_transfer).do_transfer()
        return True

    # pylint: disable=api-one-deprecated
    @api.one
    def _compute_state(self):
        # Mark as done picking transfered without any line
        if not self.move_lines and self.printed:
            self.state = "done"
            return None
        return super(StockPicking, self)._compute_state()
