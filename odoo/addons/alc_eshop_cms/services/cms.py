# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from werkzeug.exceptions import NotFound

from odoo.addons.base_rest import restapi
from odoo.addons.component.core import Component

DEMO_DATA = {
    "fr/news/my_news": {
        "type": "news",
        "lang": "fr",
        "id": 1,
        "url": "fr/news/my_news",
        "data": {"title": "Ma nouvelle", "content": "<p> Ceci est une news </p>"},
    },
    "fr/frag/the_frag": {
        "type": "frag",
        "lang": "fr",
        "id": 1,
        "url": "fr/frag/the_frag",
        "data": {"code": "footer_info", "content": "<p> Un élément du footer </p>"},
    },
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

    @restapi.method(
        [(["/content"], "GET")],
        output_param=restapi.CerberusValidator("_content_search_output_schema"),
        auth="public",
    )
    def content_search(self, **params):
        """Get all cms content"""
        return {"size": len(DEMO_DATA), "data": DEMO_DATA.values()}

    @restapi.method(
        [(["/content/<string:lang>/<string:type_prefix>/<path:url>"], "GET")],
        output_param=restapi.CerberusValidator("_content_schema"),
        auth="public",
    )
    def content_get(self, lang, type_prefix, url):
        """Get specific cms content"""
        content_key = "/".join([lang, type_prefix, url])
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
        return ["page", "news", "frag"]

    def _get_allowed_lang(self):
        installed = self.env["res.lang"].get_installed()
        # return fr from fr_BE, ...
        return [i[0].split("_")[0] for i in installed]

    # ##############
    # implementation
    # ##############
