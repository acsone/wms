# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import timedelta

from odoo import api, fields, models


class StockReleaseChannel(models.Model):

    _inherit = "stock.release.channel"
    process_end_time_delay = fields.Integer(
        compute="_compute_process_end_time_delay", store=True, readonly=False
    )

    @api.depends("warehouse_id")
    def _compute_process_end_time_delay(self):
        for rec in self:
            if not rec.process_end_time_delay:
                rec.process_end_time_delay = (
                    rec.warehouse_id.release_channel_process_end_time_delay
                )

    def _get_process_end_time_delay(self, warehouse):
        self.ensure_one()
        if self.process_end_time_delay:
            return self.process_end_time_delay
        if not warehouse:
            return 0
        if warehouse.release_channel_process_end_time_delay:
            return warehouse.release_channel_process_end_time_delay
        return warehouse.company_id.release_channel_process_end_time_delay

    def _get_shipment_advice_arrival_date(self, warehouse):
        self.ensure_one()
        process_end_time_delay = self._get_process_end_time_delay(warehouse)
        return self.process_end_date + timedelta(minutes=process_end_time_delay)
