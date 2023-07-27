# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.alc_stock_release_channel_deliver.models.stock_picking import (
    StockPicking as Picking,
)


class StockPicking(Picking):
    def _action_done(self):
        for rec in self:
            if rec.planned_shipment_advice_id.in_release_channel_auto_process:
                rec._check_shipping_cost()
        return super()._action_done()
