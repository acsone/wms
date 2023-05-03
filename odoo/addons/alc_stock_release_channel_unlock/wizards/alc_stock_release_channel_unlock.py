# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models

from odoo.addons.alc_stock_release_channel_tag.models.alc_stock_release_channel_tag import (
    AlcStockReleaseChannelTag,
)


class AlcStockReleaseChannelUnlock(models.TransientModel):

    _name = "alc.stock.release.channel.unlock"
    _description = "Alc Stock Release Channel Unlock Wizard"

    stock_release_channel_tag_ids = fields.Many2many[AlcStockReleaseChannelTag](
        string="Release channel tags",
        relation="stock_release_channel_unlock_tag_rel",
        required=True,
    )

    def _get_channels_to_unlock(self):
        all_channels = self.env["stock.release.channel"].search(
            [("state", "in", ("locked", "asleep"))]
        )
        return all_channels.filtered(
            lambda c: any(
                tag in c.stock_release_channel_tag_ids
                for tag in self.stock_release_channel_tag_ids
            )
        )

    def _get_channels_to_lock(self):
        return self.env["stock.release.channel"].search([("state", "=", "open")])

    def action_unlock(self):
        self.ensure_one()
        channels_to_lock = self._get_channels_to_lock()
        channels_to_lock.action_lock()
        channels_to_unlock = self._get_channels_to_unlock()
        channels_to_unlock.filtered("is_action_unlock_allowed").action_unlock()
        channels_to_unlock.filtered("is_action_wake_up_allowed").action_wake_up()
        action = self.env["ir.actions.actions"]._for_xml_id(
            "stock_release_channel.stock_release_channel_act_window"
        )
        action["context"] = {"search_default_filter_open": True}
        return action
