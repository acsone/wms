# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from collections import defaultdict

from odoo.addons.alc_eshop_cms import models


class AlcContentLangMixin(models.AlcContentLangMixin):
    def _get_content_context_lang(self, field_name=None):
        lang = self.env.lang or "en_US"
        return lang.split("_")[0]

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

    def _iter_by_lang(self, lang_ids=None):
        """Iterate over the record in specified langs if the record is available.

        into the given land

        If no lang given, iterate over all the lang specified on the records
        """
        for lang_id, records in self._get_records_by_lang().items():
            if lang_ids and lang_id not in lang_ids:
                continue
            for record in records.with_context(lang=lang_id.code):
                yield record

    def _get_records_by_lang(self):
        """Return a dict of records by lang."""
        result = defaultdict(self.browse)
        for record in self:
            for lang_id in record.lang_ids:
                result[lang_id] |= record
        return result
