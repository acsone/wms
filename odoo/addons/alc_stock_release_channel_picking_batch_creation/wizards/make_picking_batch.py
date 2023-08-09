# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.stock_picking_batch_creation.wizards.make_picking_batch import (
    MakePickingBatch as MakePickingBatchBase,
)
from odoo.addons.stock_release_channel.models.stock_release_channel import (
    StockReleaseChannel,
)


class MakePickingBatch(MakePickingBatchBase):

    release_channel_id = fields.Many2one[StockReleaseChannel](string="Release Channel")

    def _get_picking_domain_common(self):
        domain = super()._get_picking_domain_common()
        if not self.release_channel_id:
            return domain
        picking_type_ids_pick_allowed = (
            self.release_channel_id._get_all_picking_type_ids_pick_allowed()
        )
        domain.extend(
            [
                ("release_channel_id", "=", self.release_channel_id.id),
                ("release_channel_id.pick_allowed", "=", True),
                ("picking_type_id", "in", picking_type_ids_pick_allowed),
            ]
        )
        if self.user_id:
            domain.extend(
                [
                    "|",
                    ("release_channel_id.user_ids", "=", False),
                    ("release_channel_id.user_ids", "in", self.user_id.ids),
                ]
            )
        else:
            domain.extend([("release_channel_id.user_ids", "=", False)])

        return domain
