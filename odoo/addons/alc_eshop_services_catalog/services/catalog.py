# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from collections import OrderedDict

from odoo.addons.base_rest import restapi
from odoo.addons.base_rest.components.service import to_int
from odoo.addons.component.core import Component


class CatalogService(Component):

    _inherit = "base.rest.service"
    _name = "catalog.service"
    _collection = "shopinvader.backend"
    _usage = "catalog"

    @restapi.method(
        [(["/"], "GET")],
        input_param=restapi.CerberusValidator("_search_input_schema"),
        output_param=restapi.CerberusValidator("_search_output_schema"),
    )
    def search(self, **params):
        domain = self._get_base_domain()
        records = self._search(domain, **params)
        return self._paginate_search_records(domain, records)

    def _search(self, domain=None, **params):
        lang = params.pop("lang", None)
        limit = params.pop("limit", None)
        per_page = params.pop("per_page", None) or limit
        domain = domain or self._get_base_domain()
        return self._records(lang, domain, per_page=per_page, **params)

    def _lang_allowed(self):
        return OrderedDict([("en", "en_US"), ("fr", "fr_BE"), ("nl", "nl_BE")])

    def _lang_allowed_output(self):
        return ["en_US", "fr_BE", "nl_BE"]

    def _search_input_schema(self):
        return {
            "page": {
                "coerce": to_int,
                "nullable": True,
                "type": "integer",
                "default": 1,
            },
            "limit": {
                "coerce": to_int,
                "nullable": True,
                "type": "integer",
                "default": None,
            },
            "lang": {
                "type": "string",
                "allowed": list(self._lang_allowed().keys()),
                "required": False,
                "nullable": True,
            },
        }

    def _get_model_schema(self):
        return {
            "id": {"type": "integer", "required": True, "nullable": False},
            "name": {"type": "string", "required": True, "nullable": False},
        }

    def _search_output_schema(self):
        return {
            "size": {"type": "integer"},
            "data": {
                "type": "list",
                "schema": {"type": "dict", "schema": self._get_model_schema()},
            },
        }

    @property
    def env(self):
        env = self.work.env
        return env

    @property
    def partner(self):
        partner = self.env["res.partner"].browse()
        partner_id = self.work.authenticated_partner_id
        if partner_id:
            partner = partner.browse(partner_id)
        return partner

    @property
    def model(self):
        return self.env["product.product"]

    def _get_lang(self, language):
        allowed = self._lang_allowed()
        language = language.lower() if language else self.partner.lang
        if language in allowed:
            return allowed[language]
        langs = allowed.values()
        return language if language in langs else langs[0]

    def _get_base_domain(self):
        return [("allowed_partner_types", "like", "%%%s%%" % self.partner.partner_type)]

    def _get(self, _id):
        domain_base = self._get_base_domain()
        domain = domain_base + [("id", "=", _id)]
        return self.model.search(domain)

    def _records(self, language, domain, page=1, per_page=10):
        offset = per_page * (page - 1) if per_page and page else 0
        lang = self._get_lang(language)
        model = self.model.with_context(lang=lang)
        return model.search(domain, limit=per_page, offset=offset)

    def _paginate_search_records(self, domain, records):
        total_count = self.model.search_count(domain)
        return {"size": total_count, "data": self._to_json(records)}

    def _paginate_search(self, language, domain, page=1, per_page=10):
        records = self._records(language, domain, page=page, per_page=per_page)
        return self._paginate_search_records(domain, records)

    def _get_parser(self):
        return ["id", "name"]

    def _to_json(self, records):
        return records.jsonify(self._get_parser())
