# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.osv.expression import AND

from odoo.addons.stock_release_channel_geoengine.models.stock_picking import (
    StockPicking as StockPickingBase,
)


class StockPicking(StockPickingBase):
    def _get_release_channel_possible_candidate_domain_channel(self):
        """
        Override the domain to get possible release channels.

        for the current picking.

        If partner has channel tags, retrieve the channels that have:
           - No tags
           - Or partner tags
        Else, retrieve channels that have no tags.
        """
        self.ensure_one()
        partner_tags = self.partner_id.stock_release_channel_tag_ids
        if not partner_tags:
            return super()._get_release_channel_possible_candidate_domain_channel()
        domain = [
            "|",
            ("stock_release_channel_tag_ids", "=", False),
            ("stock_release_channel_tag_ids", "in", partner_tags.ids),
        ]
        return AND(
            [super()._get_release_channel_possible_candidate_domain_channel(), domain]
        )
