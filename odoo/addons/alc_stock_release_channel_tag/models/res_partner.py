# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.stock_release_channel_geoengine.models.res_partner import (
    ResPartner as ResPartnerBase,
)

from .alc_stock_release_channel_tag import AlcStockReleaseChannelTag


class ResPartner(ResPartnerBase):

    stock_release_channel_tag_ids = fields.Many2many[AlcStockReleaseChannelTag](
        string="Release channel tags"
    )
