# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)

try:
    from slugify import slugify
except ImportError:
    _logger.debug("Cannot `import slugify`.")


class AlcContentUrlMixin(models.AbstractModel):

    _name = "alc.content.url.mixin"
    _inherit = "alc.cms.mixin"

    name = fields.Char(required=True, translate=True)
    url = fields.Char(compute="_compute_url")

    def _get_url_parts(self):
        return [self.name]

    @api.depends("name")
    def _compute_url(self):
        for rec in self:
            parts = rec._get_url_parts()
            parts = [slugify(p) for p in parts]
            parts.append(str(rec.id))
            rec.url = "-".join(parts)

    @api.model
    def _get_from_url(self, url):
        _id = url.split("-")[-1]
        return self.search([("id", "=", int(_id))])
