# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class ShipmentAdvicePlanner(models.TransientModel):

    _inherit = "shipment.advice.planner"

    def _prepare_shipment_advice_common_vals(self, warehouse):
        self.ensure_one()
        vals = super()._prepare_shipment_advice_common_vals(warehouse)
        if self.release_channel_id:
            vals[
                "arrival_date"
            ] = self.release_channel_id._get_shipment_advice_arrival_date()
        return vals
