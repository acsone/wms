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
        qty = quantity  # not affected by number_labels_to_print
        if qty:
            report = "specific_print.report_lot_label"
            hw_print(self, report, qty=qty, printer_id=printer_id)
