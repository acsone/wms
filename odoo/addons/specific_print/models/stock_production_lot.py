# -*- coding: utf-8 -*-
# © 2016-2017 Jacques-Etienne Baudoux (BCIM)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models

from ..utils import hw_print


class StockProductionLot(models.Model):
    _inherit = "stock.production.lot"

    @api.multi
    def print_lot_label(self, quantity=1, printer_id=False):
        self.ensure_one()
        hw_print(
            self, "specific_print.report_lot_label", qty=quantity, printer_id=printer_id
        )
