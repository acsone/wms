# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

from . import AlcEshopCmsPageGroup, AlcEshopCmsPageSlot


class AlcEshopCmsPage(models.Model):
    _name = "alc.eshop.cms.page"
    _inherit = [  # nosemgrep: is-old-style-inheritance
        "alc.content.lang.mixin",
        "alc.content.image.mixin",
    ]
    _description = "CMS Page"
    _content_type = "page"
    _order = "sequence, id desc"

    sequence = fields.Integer(default=0)
    published = fields.Boolean()
    cms_page_group_id = fields.Many2one[AlcEshopCmsPageGroup](
        string="Group",
        required=True,
    )
    cms_page_slot_ids = fields.Many2many[AlcEshopCmsPageSlot](string="Slots")

    def _get_url_parts(self):
        return [self.cms_page_group_id.name, *super()._get_url_parts()]

    @api.model
    def _get_contents_published(self):
        return self.search([("published", "=", True)])
