# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.stock_release_channel.models.stock_release_channel import (
    StockReleaseChannel as StockReleaseChannelBase,
)


class StockReleaseChannel(StockReleaseChannelBase):

    _inherit = "stock.release.channel"

    def print_all_deliveryslip(self):
        done_shipment_advices = self.in_process_shipment_advice_ids.filtered(
            lambda s: s.state == "done"
        )
        return done_shipment_advices.print_all_deliveryslip()
