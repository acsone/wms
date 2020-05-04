# -*- coding: utf-8 -*-
# © 2017 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def button_receive(self):
        self.ensure_one()

        if not self.operator_id:
            self.assign_operator()

        return self.env.ref("stock_receive_lot.action_pack_operation_lot_add").read()[0]
