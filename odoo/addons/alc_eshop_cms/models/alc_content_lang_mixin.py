# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from collections import defaultdict

from odoo import api, fields, models


class AlcContentLangMixin(models.AbstractModel):

    _name = "alc.content.lang.mixin"
    _inherit = "alc.content.url.mixin"
    _content_type = ""

    lang_ids = fields.Many2many("res.lang", string="Lang", required=True)

    @api.model
    def _get_parser(self):
        return [
            "id",
            ("type", lambda a, f: a._content_type),
            ("url", "_get_content_url"),
            ("lang", "_get_content_context_lang"),
        ]

    @api.model
    def _get_data_parser(self):
        return []

    def _get_content_context_lang(self, field_name=None):
        return self.env.lang.split("_")[0]

    def _get_content_url(self, field_name=None):
        self.ensure_one()
        return "/".join(
            [self._get_content_context_lang(), self._content_type, self.url]
        )

    def _to_json(self, lang_ids=None):
        """Return a list of json for each record

        If a list of lang is specified, we only return json for records for each
        lang of the given record
        """
        result = []
        records_by_lang = defaultdict(self.browse)
        parser = self._get_parser()
        data_parser = self._get_data_parser()
        for record in self:
            for lang_id in record.lang_ids:
                if lang_ids and lang_id not in lang_ids:
                    continue
                records_by_lang[lang_id] |= record
        for lang_id, records in records_by_lang.items():
            for record in records.with_context(lang=lang_id.code):
                json = record.jsonify(parser=parser, one=True)
                json["data"] = record.jsonify(parser=data_parser, one=True)
                result.append(json)
        return result
