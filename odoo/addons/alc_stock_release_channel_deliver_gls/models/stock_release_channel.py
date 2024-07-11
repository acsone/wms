# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.stock_release_channel_shipment_advice_deliver.models.stock_release_channel import (
    StockReleaseChannel as StockReleaseChannelBase,
)


class StockReleaseChannel(StockReleaseChannelBase):
    def action_deliver(self):
        if "gls" in self.mapped("picking_to_plan_ids.delivery_type"):
            action = self.env["ir.actions.actions"]._for_xml_id(
                "stock.action_picking_tree_all"
            )
            action["domain"] = [("id", "in", self.picking_to_plan_ids.ids)]
            return action
        return super().action_deliver()
