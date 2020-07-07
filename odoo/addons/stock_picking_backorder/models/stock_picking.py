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

    def _compute_is_action_force_transfer_allowed(self):
        has_group = self.user_has_groups("base.group_no_one")
        for rec in self:
            rec.is_action_force_transfer_allowed = has_group and (
                rec.state in ("draft,partially_available,assigned")
                or rec.is_create_backorder_allowed
            )

    def _compute_is_create_backorder_allowed(self):
        for rec in self:
            # allow to transfer and create backorder even if no line
            # processed
            rec.is_create_backorder_allowed = rec._is_create_backorder_allowed()

    def _is_create_backorder_allowed(self):
        self.ensure_one()
        return (
            self.state == "draft"
            or all(x.qty_done == 0.0 for x in self.pack_operation_ids)
        ) and self.check_backorder()

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
            else:
                return super(StockPicking, self).do_new_transfer()
        else:
            if self.check_backorder():
                # allow to process and create backorder even if no line
                # processed
                wiz = self.env["stock.backorder.confirmation"].create(
                    {"pick_id": self.id}
                )
                wiz.process()
            else:
                return super(StockPicking, self).do_new_transfer()

        return {}

    @api.multi
    def do_transfer(self):
        to_backorder = self.filtered(lambda pick: pick._is_create_backorder_allowed())
        to_transfer = self - to_backorder
        to_backorder._create_backorder()
        super(StockPicking, to_transfer).do_transfer()
        return True

    @api.one
    def _compute_state(self):
        # Mark as done picking transfered without any line
        if not self.move_lines and self.printed:
            self.state = "done"
        else:
            super(StockPicking, self)._compute_state()
