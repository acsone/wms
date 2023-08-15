# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields

from odoo.addons.shopfloor_workstation.models.shopfloor_workstation import (
    ShopfloorWorkstation,
)
from odoo.addons.stock_picking_batch.models.stock_picking_batch import (
    StockPickingBatch as StockPickingBatchBase,
)


class StockPickingBatch(StockPickingBatchBase):

    workstation_selected = fields.Boolean(
        default=False,
        help="Technical field set to True if the workstation has already been selected",
        compute="_compute_workstation_selected",
    )

    workstation_id = fields.Many2one[ShopfloorWorkstation]()

    @api.depends("workstation_id")
    def _compute_workstation_selected(self):
        for rec in self:
            rec.workstation_selected = bool(rec.workstation_id)

    def write(self, vals):
        result = super().write(vals)
        if "workstation_id" in vals and vals["workstation_id"]:
            ws = self.env["shopfloor.workstation"].search(
                [("id", "=", vals["workstation_id"])], limit=1
            )
            for user in self.user_id:
                ws.set_as_default_on_user(user.sudo())
        return result
