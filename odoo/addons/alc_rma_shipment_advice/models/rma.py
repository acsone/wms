# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields

from odoo.addons.rma.models.rma import Rma as RmaBase
from odoo.addons.shipment_advice_planner_toursolver.models.shipment_advice import (
    ShipmentAdvice,
)
from odoo.addons.shipment_advice_planner_toursolver.models.toursolver_resource import (
    ToursolverResource,
)
from odoo.addons.shipment_advice_planner_toursolver.models.toursolver_task import (
    ToursolverTask,
)


class Rma(RmaBase):
    shipment_advice_id = fields.Many2one[ShipmentAdvice](
        store=True, compute="_compute_shipment_advice_id"
    )
    toursolver_task_id = fields.Many2one[ToursolverTask](
        store=True, related="shipment_advice_id.toursolver_task_id"
    )
    toursolver_resource_id = fields.Many2one[ToursolverResource](
        related="shipment_advice_id.toursolver_resource_id", store=True
    )

    def _create_receipt(self):
        res = super()._create_receipt()
        for rec in self:
            if rec.operation_id.exclude_from_rma_shipment_advice:
                rec.reception_move_id.picking_id.exclude_from_rma_shipment_advice = True
        return res

    @api.depends("move_id")
    def _compute_shipment_advice_id(self):
        for rec in self:
            rec.shipment_advice_id = rec.move_id.shipment_advice_id
