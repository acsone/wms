# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.osv.expression import AND, FALSE_DOMAIN

from odoo.addons.stock_picking_batch_creation.wizards.make_picking_batch import (
    MakePickingBatch as MakePickingBatchBase,
)


class MakePickingBatch(MakePickingBatchBase):

    release_channel_required = fields.Boolean(
        string="Only pickings in a release channel",
        help="Only the pickings assigned to a release channel will be selected for this batch.",
        default=False,
    )

    def _get_picking_domain_common(self):
        domain = super()._get_picking_domain_common()
        if (
            self._previous_selected_picking
            and self.user_id.only_one_release_channel_by_picking_batch
        ):
            domain = AND(
                [
                    domain,
                    [
                        (
                            "release_channel_id",
                            "=",
                            self._previous_selected_picking.release_channel_id.id,
                        )
                    ],
                ]
            )
            return domain

        if self.release_channel_required:
            channels = self.env["stock.release.channel"]._get_channels_pick_allowed(
                self.picking_type_ids
            )
            if self.user_id and self.env.context.get("restrict_to_user"):
                channels = channels.filtered(lambda c: self.user_id in c.user_ids)
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

    def _get_first_picking(self, raise_if_not_found=False):
        """Try at first to get picking from release channels related to the selected user."""
        if not self.user_id:
            return super()._get_first_picking(raise_if_not_found=raise_if_not_found)
        if self.release_channel_required:
            first_picking = super(
                MakePickingBatch, self.with_context(restrict_to_user=True)
            )._get_first_picking(raise_if_not_found=raise_if_not_found)
            if first_picking:
                return first_picking
        return super()._get_first_picking(raise_if_not_found=raise_if_not_found)
