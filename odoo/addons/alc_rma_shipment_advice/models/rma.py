# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.rma.models.rma import Rma as RmaBase


class Rma(RmaBase):
    def _create_receipt(self):
        res = super()._create_receipt()
        for rec in self:
            if rec.operation_id.exclude_from_rma_shipment_advice:
                rec.reception_move_id.picking_id.exclude_from_rma_shipment_advice = True
        return res
