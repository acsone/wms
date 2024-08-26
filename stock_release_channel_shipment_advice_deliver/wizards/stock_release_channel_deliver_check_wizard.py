# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockReleaseChannelDeliverCheckWizard(models.TransientModel):

    _name = "stock.release.channel.deliver.check.wizard"
    _description = "stock release channel deliver check wizard"

    release_channel_id = fields.Many2one("stock.release.channel")
    allowed_to_unrelease_picking_ids = fields.One2many(
        comodel_name="stock.picking",
        compute="_compute_allowed_to_unrelease_picking_ids",
        string="Current pickings that will be unreleased",
    )

    @api.depends("release_channel_id")
    def _compute_allowed_to_unrelease_picking_ids(self) -> None:
        """
        Compute the pickings that are allowed to be unreleased.
        This can show the user the possible ones that could be delivered.
        """
        for wizard in self:
            moves_to_unrelease = (
                wizard.release_channel_id._shipping_moves_to_unrelease()
            )
            wizard.allowed_to_unrelease_picking_ids = moves_to_unrelease.filtered(
                "unrelease_allowed"
            ).picking_id

    def action_deliver(self):
        self.ensure_one()
        self.release_channel_id.unrelease_picking()
        return self.release_channel_id.action_deliver()
