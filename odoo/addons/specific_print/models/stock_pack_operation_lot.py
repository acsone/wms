# -*- coding: utf-8 -*-
# © 2016-2017 Jacques-Etienne Baudoux (BCIM)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class StockPackOperationLot(models.Model):
    _inherit = "stock.pack.operation.lot"

    @api.multi
    def print_lot_label(self, quantity=1):
        self.ensure_one()
        self.lot_id.print_lot_label()
