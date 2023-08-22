# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.osv.expression import AND, FALSE_DOMAIN

from odoo.addons.stock_picking_batch_creation.wizards.make_picking_batch import (
    MakePickingBatch as MakePickingBatchBase,
)


class MakePickingBatch(MakePickingBatchBase):

    restrict_to_same_release_channel = fields.Boolean(
        string="Restrict to the same release channel",
        help="Only the pickings with the same release channel will be selected for this batch.",
    )

    def _get_picking_domain_common(self):
        domain = super()._get_picking_domain_common()
        if self.restrict_to_same_release_channel:
            channels = self.env["stock.release.channel"]._get_channels_pick_allowed(
                self.picking_type_ids
            )
            if not channels:
                domain = AND([domain, FALSE_DOMAIN])
            else:
                domain = AND(
                    [
                        domain,
                        [
                            ("release_channel_id", "in", channels.ids),
                            "|",
                            ("release_channel_id.user_ids", "=", False),
                            ("release_channel_id.user_ids", "in", self.user_id.ids),
                        ],
                    ]
                )
        return domain

    def _get_picking_domain_for_additional(self):
        domain = super()._get_picking_domain_for_additional()
        if self.restrict_to_same_release_channel:
            previous_picking = self._previous_selected_picking
            domain = AND(
                [
                    domain,
                    [
                        (
                            "release_channel_id",
                            "=",
                            previous_picking.release_channel_id.id,
                        ),
                        "|",
                        ("release_channel_id.user_ids", "=", False),
                        ("release_channel_id.user_ids", "in", self.user_id.ids),
                    ],
                ]
            )
        return domain
