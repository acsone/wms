# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AlcStockReleaseChannelTag(models.Model):

    _name = "alc.stock.release.channel.tag"
    _description = "Alc Stock Release Channel Tag"

    name = fields.Char(required=True)
    code = fields.Char("Code")
    color = fields.Integer("Color")

    @api.depends("name", "code")
    def name_get(self):
        result = []
        for rec in self:
            if not self.env.context.get("short_tag_name"):
                name = rec.name
            else:
                name = rec.code or rec.name
            result.append((rec.id, name))
        return result
