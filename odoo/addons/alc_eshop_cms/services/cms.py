# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from werkzeug.exceptions import BadRequest, NotFound

from odoo.addons.base_rest import restapi
from odoo.addons.component.core import Component

DEMO_DATA = {
    "fr/page/bienvenue": {
        "type": "page",
        "lang": "fr",
        "id": 1,
        "url": "fr/page/bienvenue",
        "data": {
            "title": "Bienvenue",
            "content": "<p> Bienvenue sur le site alcyon </p>",
        },
    },
    "fr/page/commercial/equipe": {
        "type": "page",
        "lang": "fr",
        "id": 2,
        "url": "fr/page/commercial/equipe",
        "data": {
            "title": "Equipe commerciale",
            "content": "<p> Notre équipe commerciale est ... </p>",
        },
    },
}


class CmsService(Component):
    """Provides cms content."""

    _inherit = "authenticated_partner.mixin"
    _name = "cms.service"
    _collection = "shopinvader.backend"
    _usage = "cms"

    _content_model_names = ["alc.eshop.news", "alc.eshop.snippet"]

    @restapi.method(
        [(["/content"], "GET")],
        output_param=restapi.CerberusValidator("_content_search_output_schema"),
        auth="public",
    )
    def content_search(self, **params):
        """Get all cms content"""
        res = DEMO_DATA.values()
        for model_name in self._content_model_names:
            records = self.env[model_name]._get_contents_published()
            res.extend(records._to_json())
        return {"size": len(res), "data": res}

    @restapi.method(
        [(["/content/<string:lang>/<string:content_type>/<path:url>"], "GET")],
        output_param=restapi.CerberusValidator("_content_schema"),
        auth="public",
    )
    def content_get(self, lang, content_type, url):
        """Get specific cms content"""
        if lang not in self._get_allowed_lang():
            raise BadRequest("Lang '%s' not supported" % lang)
        if content_type not in self._get_allowed_content_types():
            raise BadRequest("Content type '%s' not supported" % content_type)
        content_key = "/".join([lang, content_type, url])
        for model_name in self._content_model_names:
            model = self.env[model_name]
            if model._content_type != content_type:
                continue
            record = model._get_from_url(url)
            if record:
                res_lang = self._get_lang_from_lang_prefix(lang)
                return record.with_context(lang=res_lang.code)._to_json(res_lang)[0]
        if content_key in DEMO_DATA:
            return DEMO_DATA[content_key]
        raise NotFound(content_key)

    # #######
    # schemas
    # #######
    def _content_search_output_schema(self):
        return {
            "size": {"type": "integer"},
            "data": {
                "type": "list",
                "schema": {"type": "dict", "schema": self._content_schema()},
            },
        }

    def _content_schema(self):
        return {
            "id": {"type": "integer", "required": True, "nullable": False},
            "type": {
                "type": "string",
                "required": True,
                "nullable": False,
                "allowed": self._get_allowed_content_types(),
            },
            "lang": {
                "type": "string",
                "required": True,
                "nullable": False,
                "allowed": self._get_allowed_lang(),
            },
            "url": {"type": "string", "required": True, "nullable": False},
            "data": {"type": "dict", "required": True, "nullable": False},
        }

    def _get_allowed_content_types(self):
        return ["page", "news", "snippet"]

    def _get_allowed_lang(self):
        installed = self.env["res.lang"].get_installed()
        # return fr from fr_BE, ...
        return [i[0].split("_")[0] for i in installed]

    # ##############
    # implementation
    # ##############
    def _get_lang_from_lang_prefix(self, lang_prefix):
        all_lang = self.env["res.lang"].get_installed()
        for lang in all_lang:
            lang_code = lang[0]
            if lang_code.startswith(lang_prefix):
                return self.env["res.lang"]._lang_get(lang_code)
        return None
