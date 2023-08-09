# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields

from odoo.addons.stock_picking_batch.models.stock_picking_batch import (
    StockPickingBatch as StockPickingBatchBase,
)
from odoo.addons.stock_release_channel.models.stock_release_channel import (
    StockReleaseChannel,
)


class StockPickingBatch(StockPickingBatchBase):
    release_channel_ids = fields.Many2many[StockReleaseChannel](
        compute="_compute_release_channel_ids", string="Release Channel(s)"
    )

    @api.depends("picking_ids", "picking_ids.release_channel_id")
    def _compute_release_channel_ids(self):
        for rec in self:
            rec.release_channel_ids = rec.picking_ids.mapped("release_channel_id")
