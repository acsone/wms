# -*- coding: utf-8 -*-
# Copyright 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    @api.multi
    def action_done(self):
        res = super(StockMove, self).action_done()
        for move in self.filtered("lot_ids"):
            lots = move.lot_ids.filtered("is_archived")
            lots.write({"is_archived": False})
        return res

    def action_cancel_move(self):
        if self.picking_type_id.code != "incoming" or self.state in ["done"]:
            return
        wizard = self.env["wizard.stock.move.update.handler"].create(
            {"move_id": self.id}
        )
        wizard.action_cancel_move()
