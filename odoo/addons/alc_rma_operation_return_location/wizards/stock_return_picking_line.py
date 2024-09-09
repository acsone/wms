# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.rma.wizard.stock_picking_return import ReturnPickingLine


class StockReturnPickingLine(ReturnPickingLine):
    def _prepare_rma_vals(self):
        self.ensure_one()
        vals = super()._prepare_rma_vals()
        if self.rma_operation_id.return_location_id:
            vals["location_id"] = self.rma_operation_id.return_location_id.id
        return vals
