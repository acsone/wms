# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models

from odoo.addons.stock_release_channel.models.stock_release_channel import (
    StockReleaseChannel,
)


class StockReleaseChannelPreparationPlan(models.Model):

    _name = "stock.release.channel.preparation.plan"
    _description = "Stock Release Channel Preparation Plan"

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    release_channel_ids = fields.Many2many[StockReleaseChannel](
        relation="stock_release_channel_preparation_plan_rel",
        column1="plan_id",
        column2="channel_id",
        string="Release channels",
    )
