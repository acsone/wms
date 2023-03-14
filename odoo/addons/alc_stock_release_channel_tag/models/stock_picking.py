# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.stock_release_channel_geoengine.models.stock_picking import (
    StockPicking as StockPickingBase,
)


class StockPicking(StockPickingBase):
    def _get_release_channel_possible_candidate_domain(self):
        self.ensure_one()
        partner_tags = self.partner_id.stock_release_channel_tag_ids
        return super()._get_release_channel_possible_candidate_domain() + [
            "|",
            ("stock_release_channel_tag_ids", "=", False),
            ("stock_release_channel_tag_ids", "in", partner_tags.ids),
        ]
