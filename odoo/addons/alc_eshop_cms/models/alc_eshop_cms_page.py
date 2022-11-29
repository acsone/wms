# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AlcEshopCmsPage(models.Model):

    _inherit = ["alc.content.lang.mixin", "alc.content.image.mixin"]
    _name = "alc.eshop.cms.page"
    _content_type = "page"
    _order = "sequence, id desc"

    sequence = fields.Integer(default=0)
    published = fields.Boolean()
    cms_page_group_id = fields.Many2one(
        string="Group", comodel_name="alc.eshop.cms.page.group", required=True,
    )
    cms_page_slot_ids = fields.Many2many(
        string="Slots", comodel_name="alc.eshop.cms.page.slot"
    )

    def _get_url_parts(self):
        return [self.cms_page_group_id.name] + super(
            AlcEshopCmsPage, self
        )._get_url_parts()

    @api.model
    def _get_data_parser(self):
        res = super(AlcEshopCmsPage, self)._get_data_parser()
        res.extend(
            [
                "name:title",
                ("content", "_get_content"),
                "sequence",
                ("group", "_get_group"),
                ("slots", "_get_slots"),
            ]
        )
        return res

    def _get_group(self, fn):
        return self.cms_page_group_id.name

    def _get_slots(self, fn):
        return self.cms_page_slot_ids.mapped("name")

    @api.model
    def _get_contents_published(self):
        return self.search([("published", "=", True)])
