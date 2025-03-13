# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import date, timedelta

from odoo import fields, models


class AlcStockMoveReportWizard(models.TransientModel):

    _name = "alc.stock.move.report.wizard"
    _description = "Stock Move Report Wizard to select statistics period"

    def _default_date_end(self):
        # set default dates for previous month
        today = date.today()
        return today.replace(day=1) - timedelta(days=1)

    def _default_date_start(self):
        # set default dates for previous month
        date_end = self._default_date_end()
        return date_end.replace(day=1)

    date_start = fields.Date("Start date", default=_default_date_start, required=True)
    date_end = fields.Date("End date", default=_default_date_end, required=True)

    def action_open_sale_statistics(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "alc_sale_statistics.action_stock_moves_with_partner"
        )
        action["context"] = {
            "stat_period_date_start": self.date_start,
            "stat_period_date_end": self.date_end,
            "search_default_filter_ask_sale_statistics": 1,
            "search_default_customer_related_stock_moves": 1,
            "search_default_stat_period": 1,
        }
        action["search_view_id"] = [
            self.env.ref("alc_sale_statistics.stock_moves_with_partner_view_search").id
        ]
        return action
