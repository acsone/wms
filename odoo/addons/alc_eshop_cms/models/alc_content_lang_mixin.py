# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from collections import defaultdict

from odoo import api, fields

from odoo.addons.base.models.res_lang import Lang

from . import AlcContentUrlMixin


class AlcContentLangMixin(AlcContentUrlMixin):

    _name = "alc.content.lang.mixin"
    _description = "Alc Content Lang Mixin"
    _content_type = ""

    lang_ids = fields.Many2many[Lang](string="Lang", required=True)
    url_locales = fields.Json(compute="_compute_url_locales")

    @api.depends("url", "lang_ids")
    def _compute_url_locales(self):
        result = defaultdict(dict)
        for lang_id, records in self._get_records_by_lang().items():
            for record in records.with_context(lang=lang_id.code):
                result[record.id][lang_id.code] = record.url
        for rec in self:
            rec.url_locales = result[rec.id]
