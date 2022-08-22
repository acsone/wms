# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AlcEshopCmsNews(models.Model):

    _inherit = ["alc.content.lang.mixin", "mixin.file.id", "mixin.image.id"]
    _name = "alc.eshop.cms.news"
    _content_type = "news"
    _order = "date_start desc, id desc"

    thumbnail_image_id = fields.Many2one(
        string="storage image", comodel_name="storage.image"
    )
    thumbnail_image = fields.Binary(
        compute="_compute_thumbnail_image", inverse="_inverse_thumbnail_image"
    )
    thumbnail_image_filename = fields.Char()
    thumbnail_image_url = fields.Char(related="thumbnail_image_id.url")
    thumbnail_image_small_url = fields.Char(
        related="thumbnail_image_id.image_small_url"
    )
    thumbnail_image_medium_url = fields.Char(
        related="thumbnail_image_id.image_medium_url"
    )
    image = fields.Binary(required=False)
    foreword = fields.Html(required=True, translate=True, sanitize=False)
    content = fields.Html(required=True, translate=True, sanitize=False)
    date_start = fields.Date(required=True)
    date_end = fields.Date(required=True)

    filename = fields.Char(related=False)

    @api.depends("thumbnail_image_id")
    def _compute_thumbnail_image(self):
        for rec in self:
            rec.thumbnail_image = rec.thumbnail_image_id.data

    def _inverse_thumbnail_image(self):
        for rec in self:
            image = rec.thumbnail_image
            if rec.thumbnail_image_id:
                rec.thumbnail_image_id.with_context(
                    cleanning_storage_file=True
                ).sudo().unlink()
            if not image:
                rec.thumbnail_image_id = None
                rec.thumbnail_image_filename = None
                return
            rec.thumbnail_image_id = rec.thumbnail_image_id.create(
                {
                    "backend_id": rec._get_default_backend_id(),
                    "name": rec.thumbnail_image_filename or u"thumb_" + rec.name,
                    "data": image,
                }
            )

    def unlink(self):
        self.mapped("thumbnail_image_id").sudo().unlink()
        return super(AlcEshopCmsNews, self).unlink()

    @api.constrains("date_start", "date_end")
    def _validate_dates(self):
        for this in self:
            start = fields.Datetime.from_string(this.date_start)
            end = fields.Datetime.from_string(this.date_end)
            if start > end:
                raise ValidationError(
                    _("The defined period is not a valid (%s > %s)")
                    % (this.date_start, this.date_end)
                )

    @api.model
    def _get_data_parser(self):
        return [
            "name:title",
            "foreword",
            "content",
            ("thumbnail_image_id:thumbnail", ["name", "url", "alt_name"]),
            ("image_id:image", ["name", "url", "alt_name"]),
            ("file_id:file", ["name", "url", "mimetype"]),
        ]

    @api.model
    def _get_contents_published(self):
        today = fields.Date.today()
        return self.search([("date_start", "<=", today), ("date_end", ">=", today)])
