# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.stock_release_channel.models.stock_release_channel import (
    StockReleaseChannel as StockReleaseChannelBase,
)

from .stock_release_channel_preparation_plan import StockReleaseChannelPreparationPlan


class StockReleaseChannel(StockReleaseChannelBase):

    preparation_plan_ids = fields.Many2many[StockReleaseChannelPreparationPlan](
        relation="stock_release_channel_preparation_plan_rel",
        column1="channel_id",
        column2="plan_id",
        string="Preparation Plans",
    )
