# -*- coding: utf-8 -*-
# Copyright 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, models
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def action_uncancel(self):
        """ Try to recover a canceled picking """
        self.mapped("move_lines").write({"state": "confirmed"})
        self.mapped("move_lines").action_assign()

    def action_cancel(self):
        codes = self.mapped("picking_type_code")
        if "outgoing" in codes or "PICK" in self.mapped("picking_type_subcode"):
            if not self.user_has_groups("stock_constraint.group_picking_cancel"):
                raise UserError(_("You are not allowed to cancel such operation"))
        return super(StockPicking, self).action_cancel()

    def do_transfer(self):
        """ Prevent button to be clicked twice as this will perform the action
        twice """
        if not self:
            return True
        self.env.cr.execute(
            "SELECT state FROM stock_move WHERE picking_id in %s " "FOR UPDATE NOWAIT",
            (tuple(self.ids),),
        )
        to_do = self.filtered(lambda p: p.state not in ("cancel", "done"))
        if to_do:
            return super(StockPicking, to_do).do_transfer()
        return True


class StockMove(models.Model):
    _inherit = "stock.move"

    def action_cancel(self):
        """ Prevent to cancel a move from a printed picking """
        if self.filtered("picking_id.printed") and not self.env.context.get(
            "force_cancel"
        ):
            raise UserError(
                _("You cannot cancel a move that is part of a started picking")
            )
        return super(StockMove, self).action_cancel()

    def action_done(self):
        """ Prevent to do a move twice """
        if not self:
            return True
        self.env.cr.execute(
            "SELECT state FROM stock_move WHERE id in %s " "FOR UPDATE NOWAIT",
            (tuple(self.ids),),
        )
        to_do = self.filtered(lambda m: m.state not in ("cancel", "done"))
        if to_do:
            return super(StockMove, to_do).action_done()
        return True
