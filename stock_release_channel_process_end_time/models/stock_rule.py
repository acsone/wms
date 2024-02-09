# Copyright 2019 Camptocamp (https://www.camptocamp.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class StockRule(models.Model):
    _inherit = "stock.rule"

    propagate_process_end_date_as_move_date_deadline = fields.Boolean(
        related="route_id.propagate_process_end_date_as_move_date_deadline", store=True
    )

    def _run_pull(self, procurements):
        process_end_date = self.env.context.get("release_channel_process_end_date")
        for procurement, rule in procurements:
            if (
                rule.propagate_process_end_date_as_move_date_deadline
                and process_end_date
            ):
                values = procurement.values
                values["date_deadline"] = process_end_date
        super()._run_pull(procurements)
        return True
