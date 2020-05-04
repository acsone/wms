# -*- coding: utf-8 -*-
# Copyright 2019 Iryna Vyshnevska (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import _, fields, models


class StockMoveWizard(models.TransientModel):
    _name = "wizard.stock.move.update.handler"
    _description = "Stock Move Handler"

    move_id = fields.Many2one("stock.move", readonly=True)
    new_date_expected = fields.Datetime(string="New Scheduled Date")

    def action_set_expired_date(self):
        picking = self.move_id.picking_id
        if self.new_date_expected != self.move_id.date_expected:
            nde = fields.Datetime.from_string(self.new_date_expected)
            appropriate_picking = picking.search(
                [
                    ("partner_id", "=", picking.partner_id.id),
                    ("min_date", ">=", nde.strftime("%Y-%m-%d 00:00:00")),
                    ("min_date", "<=", nde.strftime("%Y-%m-%d 23:59:59")),
                    ("state", "not in", ["done", "cancel"]),
                    ("picking_type_id.code", "=", "incoming"),
                ]
            )
            need_close_action = False
            if len(picking.move_lines) == 1:
                if not appropriate_picking:
                    # no need to create new picking
                    self.move_id.write({"date_expected": self.new_date_expected})
                    picking.write({"min_date": self.new_date_expected})
                    return {"type": "ir.actions.act_window_close"}
                else:
                    need_close_action = True
            if appropriate_picking:
                target_picking = appropriate_picking[0]
            else:
                target_picking = picking.copy(
                    {
                        "move_lines": False,
                        "pack_operation_product_ids": False,
                        "min_date": self.new_date_expected,
                    }
                )
            self.move_id.write(
                {
                    "date_expected": self.new_date_expected,
                    "picking_id": target_picking.id,
                }
            )
            if picking.move_lines:
                picking.do_prepare_partial()
            target_picking.do_prepare_partial()
            picking.message_post(
                body=_(
                    "Move for product {} with quantity {} \
                    of current picking moved to {}"
                ).format(
                    self.move_id.product_id.name,
                    self.move_id.product_qty,
                    target_picking.name,
                )
            )
            if need_close_action:
                picking.action_cancel()
                picking.write({"state": "cancel"})
        return {"type": "ir.actions.act_window_close"}

    def action_cancel_move(self):
        picking = self.move_id.picking_id
        picking.message_post(
            body=_("Move for product {} with quantity {} canceled").format(
                self.move_id.product_id.name, self.move_id.product_qty
            )
        )
        self.move_id.action_cancel()
        return {"type": "ir.actions.act_window_close"}
