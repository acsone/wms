# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.stock_release_channel_plan.models.stock_release_channel_preparation_plan import (
    StockReleaseChannelPreparationPlan as BaseStockReleaseChannelPreparationPlan,
)


class StockReleaseChannelPreparationPlan(BaseStockReleaseChannelPreparationPlan):
    def action_import_release_channels(self):
        return self.env.ref(
            "alc_stock_release_channel_import.alc_import_delivery_zone_wizard_act_window"
        ).read()[0]

    def write(self, vals):
        res = super().write(vals)
        inactive = self.filtered(lambda r: not r.active)
        inactive.release_channel_ids.write({"active": False})
        return res
