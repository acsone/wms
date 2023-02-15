# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockWarehouse(models.Model):

    _inherit = "stock.warehouse"

    release_channel_process_end_time_delay = fields.Integer(
        compute="_compute_release_channel_end_time_delay", store=True, readonly=False
    )

    @api.depends("company_id")
    def _compute_release_channel_end_time_delay(self):
        for rec in self:
            if not rec.release_channel_process_end_time_delay:
                rec.release_channel_process_end_time_delay = (
                    rec.company_id.release_channel_process_end_time_delay
                )
