# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import timedelta

from odoo import api, fields, models


class StockReleaseChannel(models.Model):

    _inherit = "stock.release.channel"
    shipment_advice_arrival_delay = fields.Integer(
        compute="_compute_shipment_advice_arrival_delay",
        store=True,
        readonly=False,
        help="The delay between the release channel process end time and the arrival "
        "of shipments to the dock.",
    )

    @api.depends("warehouse_id")
    def _compute_shipment_advice_arrival_delay(self):
        for rec in self:
            if not rec.shipment_advice_arrival_delay:
                rec.shipment_advice_arrival_delay = (
                    rec.warehouse_id.release_channel_shipment_advice_arrival_delay
                )

    def _get_shipment_advice_arrival_delay(self, warehouse):
        self.ensure_one()
        if self.shipment_advice_arrival_delay:
            return self.shipment_advice_arrival_delay
        if not warehouse:
            return 0
        if warehouse.release_channel_shipment_advice_arrival_delay:
            return warehouse.release_channel_shipment_advice_arrival_delay
        return warehouse.company_id.release_channel_shipment_advice_arrival_delay

    def _get_shipment_advice_arrival_date(self, warehouse):
        self.ensure_one()
        shipment_advice_arrival_delay = self._get_shipment_advice_arrival_delay(
            warehouse
        )
        return self.process_end_date + timedelta(minutes=shipment_advice_arrival_delay)
