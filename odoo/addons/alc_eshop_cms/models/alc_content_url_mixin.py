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

    name = fields.Char(required=True, translate=True)
    url = fields.Char(compute="_compute_url")

    @api.depends("name")
    def _compute_url(self):
        for rec in self:
            rec.url = "-".join([slugify(rec.name), str(rec.id)])

    @api.model
    def _get_from_url(self, url):
        _id = url.split("-")[-1]
        return self.search([("id", "=", int(_id))])
