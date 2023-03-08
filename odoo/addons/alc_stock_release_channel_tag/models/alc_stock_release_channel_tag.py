# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AlcStockReleaseChannelTag(models.Model):

    _name = "alc.stock.release.channel.tag"
    _description = "Alc Stock Release Channel Tag"

    name = fields.Char(required=True)
