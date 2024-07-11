# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.stock_release_channel_shipment_advice_deliver.models.shipment_advice import (
    ShipmentAdvice as ShipmentAdviceBase,
)


class ShipmentAdvice(ShipmentAdviceBase):
    def _generate_optimization_operational_export_request(self):
        self.ensure_one()
        return {
            "taskId": self.toursolver_task_id.task_id,
            "resourceMapping": [
                {
                    "id": r.resource_id,
                    "operationalId": f"{r.resource_id.lower()}@alcyonbelux.be",
                }
                for r in self.toursolver_task_id.delivery_resource_ids
            ],
            "force": True,  # override if exists
            "startDate": self.departure_date.strftime("%Y-%m-%d"),
            "dayNums": [1],
        }
