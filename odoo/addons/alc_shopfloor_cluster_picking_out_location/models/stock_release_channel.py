# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.stock_release_channel_shipment_advice_deliver.models.stock_release_channel import (
    StockReleaseChannel as StockReleaseChannelBase,
)


class StockReleaseChannel(StockReleaseChannelBase):
    def _action_deliver(self):
        res = super()._action_deliver()
        out_location = self.env.ref("stock.stock_location_output")
        out_locations_to_clean = self.env["stock.location"].search(
            [
                ("id", "child_of", out_location.id),
                ("release_channel_id", "in", self.ids),
            ]
        )
        out_locations_to_clean.write({"release_channel_id": None})
        return res
