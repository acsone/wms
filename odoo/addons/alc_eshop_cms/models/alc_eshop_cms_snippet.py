# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AlcEshopCmsSnippet(models.Model):
    _name = "alc.eshop.cms.snippet"
    _inherit = [  # nosemgrep: is-old-style-inheritance
        "alc.content.lang.mixin",
        "alc.content.image.mixin",
    ]
    _description = "CMS Snippet"
    _content_type = "snippet"

    name = fields.Char(translate=False)
    code = fields.Char(required=True)

    @api.model
    def _get_contents_published(self):
        return self.search([])
