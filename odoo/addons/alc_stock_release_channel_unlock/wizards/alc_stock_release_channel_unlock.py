# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from datetime import datetime

from odoo import fields, models

from odoo.addons.alc_stock_release_channel_preparation_plan.models.stock_release_channel_preparation_plan import (
    StockReleaseChannelPreparationPlan,
)
from odoo.addons.alc_stock_release_channel_tag.models.alc_stock_release_channel_tag import (
    AlcStockReleaseChannelTag,
)
from odoo.addons.partner_tz.tools.tz_utils import tz_to_utc_naive_datetime
from odoo.addons.stock_release_channel_process_end_time.utils import float_to_time


class AlcStockReleaseChannelUnlock(models.TransientModel):

    _name = "alc.stock.release.channel.unlock"
    _description = "Alc Stock Release Channel Unlock Wizard"

    stock_release_channel_tag_ids = fields.Many2many[AlcStockReleaseChannelTag](
        string="Release channel tags", relation="stock_release_channel_unlock_tag_rel"
    )
    preparation_plan_id = fields.Many2one[StockReleaseChannelPreparationPlan](
        string="Preparation Plan", required=True
    )
    process_end_date = fields.Datetime(required=True)

    def _get_channels_to_unlock_domain(self):
        self.ensure_one()
        return [
            ("state", "in", ("locked", "asleep")),
            "|",
            (
                "stock_release_channel_tag_ids",
                "in",
                self.stock_release_channel_tag_ids.ids,
            ),
            ("stock_release_channel_tag_ids", "=", False),
            "|",
            (
                "preparation_plan_ids",
                "in",
                self.preparation_plan_id.ids,
            ),
            ("preparation_plan_ids", "=", False),
        ]

    def _get_channels_to_unlock(self):
        return self.env["stock.release.channel"].search(
            self._get_channels_to_unlock_domain()
        )

    def action_unlock(self):
        self.ensure_one()
        channels_to_unlock = self._get_channels_to_unlock()
        channels_to_unlock.filtered("is_action_unlock_allowed").action_unlock()
        channels_to_unlock.filtered("is_action_wake_up_allowed").action_wake_up()
        for channel in channels_to_unlock:
            end_time = float_to_time(channel.process_end_time)  # in TZ
            end_date = datetime.combine(self.process_end_date, end_time)  # in TZ
            tz = channel.process_end_time_tz or "UTC"
            end_date_utc = tz_to_utc_naive_datetime(tz, end_date)
            channel.process_end_date = end_date_utc

        action = self.env["ir.actions.actions"]._for_xml_id(
            "stock_release_channel.stock_release_channel_act_window"
        )
        action["context"] = {
            "search_default_filter_open": True,
            "search_default_filter_locked": True,
            "search_default_filter_delivering": True,
        }
        return action
