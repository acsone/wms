# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AlcEshopCmsSnippet(models.Model):

    _inherit = ["alc.content.lang.mixin", "mixin.image.id"]
    _name = "alc.eshop.cms.snippet"
    _content_type = "snippet"

    name = fields.Char(translate=False)
    code = fields.Char(required=True)
    content = fields.Html(required=True, translate=True, sanitize=False)
    image = fields.Binary(required=False)

    @api.model
    def _get_data_parser(self):
        return [
            "code",
            "content",
            "image",
        ]

    @api.model
    def _get_contents_published(self):
        return self.search([])
