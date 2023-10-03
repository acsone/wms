# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.stock_release_channel.models.stock_release_channel import (
    StockReleaseChannel as StockReleaseChannelBase,
)


class StockReleaseChannel(StockReleaseChannelBase):

    _inherit = "stock.release.channel"

    def print_all_deliveryslip(self):
        shipment_advice = self.shipment_advice_ids.filtered(
            "in_release_channel_auto_process"
        )
        if not shipment_advice:
            return {}
        if len(shipment_advice) > 1:
            shipment_advice = shipment_advice[0]
        return shipment_advice.print_all_deliveryslip()
