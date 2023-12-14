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

    def _get_picking_domain_for_additional(self):
        domain = super()._get_picking_domain_for_additional()
        if self.restrict_to_same_release_channel:
            previous_picking = self._previous_selected_picking
            release_channel = previous_picking.release_channel_id
            domain = AND([domain, [("release_channel_id", "=", release_channel.id)]])
        return domain

    def _get_first_picking(self, no_nbr_lines_limit=False):
        """Try at first to get picking from release channels related to the selected user."""
        if not self.user_id:
            return super()._get_first_picking(no_nbr_lines_limit=no_nbr_lines_limit)
        first_picking = super(
            MakePickingBatch, self.with_context(restrict_to_user=True)
        )._get_first_picking(no_nbr_lines_limit=no_nbr_lines_limit)
        if first_picking:
            return first_picking
        return super()._get_first_picking(no_nbr_lines_limit=no_nbr_lines_limit)
