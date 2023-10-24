# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from odoo.addons.fs_file.fields import FSFile
from odoo.addons.fs_image.fields import FSImage


class AlcEshopCmsNews(models.Model):
    _name = "alc.eshop.cms.news"
    _inherit = [  # nosemgrep: is-old-style-inheritance
        "alc.content.lang.mixin",
        "fs.image.mixin",
        "mixin.past",
    ]
    _description = "CMS News"
    _content_type = "news"
    _order = "date_start desc, id desc"

    file = FSFile()
    thumbnail_image = FSImage()
    foreword = fields.Html(required=True, translate=True, sanitize=False)
    content = fields.Html(required=True, translate=True, sanitize=False)
    date_start = fields.Date(required=True)
    date_end = fields.Date(required=True)

    @api.constrains("date_start", "date_end")
    def _validate_dates(self):
        for this in self:
            if this.date_start > this.date_end:
                raise ValidationError(
                    _(
                        "The defined period is not a valid (%(date_start)s > %(date_end)s",
                        date_start=this.date_start,
                        date_end=this.date_end,
                    )
                )

    @api.model
    def _get_contents_published(self):
        today = fields.Date.today()
        return self.search([("date_start", "<=", today), ("date_end", ">=", today)])
