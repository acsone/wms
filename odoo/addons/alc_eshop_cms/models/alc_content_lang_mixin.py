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
    url_locales = fields.Serialized(compute="_compute_url_locales")

    @api.depends("url", "lang_ids")
    def _compute_url_locales(self):
        result = defaultdict(dict)
        for lang_id, records in self._get_records_by_lang().items():
            for record in records.with_context(lang=lang_id.code):
                result[record.id][lang_id.code] = record.url
        for rec in self:
            rec.url_locales = result[rec.id]

    @api.model
    def _get_parser(self):
        return [
            "id",
            ("type", lambda a, f: a._content_type),
            ("url", "_get_content_url"),
            ("url_locales", "_get_content_url_locales"),
            ("lang", "_get_content_context_lang"),
        ]

    def _get_content_context_lang(self, field_name=None):
        return self.env.lang.split("_")[0]

    def _get_content_url(self, field_name=None):
        self.ensure_one()
        return "/".join(
            [self._get_content_context_lang(), self._content_type, self.url]
        )

    def _get_content_url_locales(self, field_name=None):
        self.ensure_one()
        res = {}
        for lang_id in self.lang_ids:
            url = self.url_locales.get(lang_id.code, False)
            lang = lang_id.code.split("_")[0]
            res[lang] = "/".join([lang, self._content_type, url])
        return res

    def _to_json(self, lang_ids=None):
        """Return a list of json for each record

        If a list of lang is specified, we only return json for records for each
        lang of the given record
        """
        result = []
        parser = self._get_parser()
        data_parser = self._get_data_parser()
        for lang_id, records in self._get_records_by_lang().items():
            if lang_ids and lang_id not in lang_ids:
                continue
            for record in records.with_context(lang=lang_id.code):
                json = record.jsonify(parser=parser, one=True)
                json["data"] = record.jsonify(parser=data_parser, one=True)
                result.append(json)
        return result

    def _get_records_by_lang(self):
        """Return a dict of records by lang"""
        result = defaultdict(self.browse)
        for record in self:
            for lang_id in record.lang_ids:
                result[lang_id] |= record
        return result
