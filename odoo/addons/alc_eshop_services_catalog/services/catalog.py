# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from collections import OrderedDict

from werkzeug.exceptions import NotFound

from odoo.addons.base_rest import restapi
from odoo.addons.base_rest.components.service import to_int
from odoo.addons.component.core import Component


class CatalogService(Component):

    _inherit = [
        "authenticated_partner.mixin",
        "standard.service.mixin",
        "paginated.service.mixin",
    ]
    _name = "catalog.service"
    _collection = "shopinvader.backend"
    _usage = "catalog"

    @restapi.method(
        [(["/"], "GET")],
        input_param=restapi.CerberusValidator("_search_input_schema"),
        output_param=restapi.CerberusValidator("_paginated_output_schema"),
    )
    def search(self, page=1, per_page=10, **params):
        vals = self._process_params(params, "search")
        per_page = params.pop("limit", per_page)
        domain = self._get_domain("search", vals)
        args = {"per_page": per_page, "page": page}
        domain = self.model._product_domain_to_model_domain(domain)
        records = self._search(domain, **args)
        count = self.model.search_count(domain)
        return self._paginate_result(count, self._process_records(records, "output"))

    def _search(self, domain=None, **params):
        lang = params.pop("lang", None)
        limit = params.pop("limit", None)
        per_page = params.pop("per_page", None) or limit
        domain = domain or self._get_base_domain()
        domain = self.model._product_domain_to_model_domain(domain)
        return self._records(lang, domain, per_page=per_page, **params)

    def _lang_allowed(self):
        return OrderedDict([("en", "en_US"), ("fr", "fr_BE"), ("nl", "nl_BE")])

    def _lang_allowed_output(self):
        return ["en_US", "fr_BE", "nl_BE"]

    @property
    def model(self):
        return self.env["alc.product.flattened.data"]

    def _get_lang(self, language):
        allowed = self._lang_allowed()
        language = language.lower() if language else self.partner.lang
        if language in allowed:
            return allowed[language]
        langs = allowed.values()
        return language if language in langs else langs[0]

    def _get_base_domain(self, keyword=None):  # for standard_service signature
        return self.partner._get_product_domain()

    def _get(self, reference, language=False):
        domain_base = self._get_base_domain()
        domain = domain_base + [("default_code", "=", reference)]
        lang = self._get_lang(language)
        product = next(self._records(lang, domain), None)
        if not product:
            raise NotFound("No product found with this reference.")
        return product

    @restapi.method(
        [(["/<string:reference>"], "GET")],
        input_param=restapi.CerberusValidator({}),
        output_param=restapi.CerberusValidator("_output_schema"),
    )
    def get_by_reference(self, reference, lang=False):
        product = self._get(reference, lang)
        return self._jsonify_row(product, "output")

    def _records(self, language, domain, page=1, per_page=10):
        offset = per_page * (page - 1) if per_page and page else 0
        lang = self._get_lang(language)
        model = self.model.with_context(lang=lang)
        return model._get_partner_products_iterator(
            self.partner, domain_extend=domain, limit=per_page, offset=offset
        )

    def _output_schema(self):
        return self._get_schema("output")

    def _search_input_schema(self):
        return self._get_schema("search", search=True)

    def _paginated_output_schema(self):
        return self._paginate_schema(self._get_schema("output"))

    def _process_records(self, records, keyword):
        return [self._jsonify_row(r, keyword) for r in records]

    def _jsonify_row(self, row, keyword=None):
        price_htva = row.gross_price
        vat = row.tax_amount
        return {
            "name": row.name,
            "reference": row.default_code,
            "category": row.categ,
            "url_key": row.url_key,
            "indicated_price": row.indicated_price,
            "vat": vat,
            "code_amm": row.code_amm or None,
            "ean_13": row.barcode or None,
            "ext_cti": row.code_cti or None,
            "manufacturer": row.manufacturer or None,
            "cnk_code": row.cnk_code or None,
            "price_htva": price_htva,
            "price_tvac": price_htva + (price_htva * vat / 100),
        }

    def _get_schema_generator(self):
        return {
            "page": {
                "coerce": to_int,
                "nullable": True,
                "type": "integer",
                "default": 1,
                "search": {},
            },
            "limit": {
                "coerce": to_int,
                "nullable": True,
                "type": "integer",
                "default": 10,
                "search": {},
            },
            "lang": {
                "type": "string",
                "allowed": list(self._lang_allowed().keys()),
                "required": False,
                "nullable": True,
                "search": {},
                "get": {},
            },
            "name": {
                "type": "string",
                "required": True,
                "nullable": False,
                "output": {},
                "search": {"required": False, "operators": ["=", "ilike"]},
            },
            "code_amm": {
                "type": "string",
                "required": True,
                "nullable": True,
                "output": {},
                "search": {"required": False, "operators": ["=", "ilike"]},
            },
            "ean_13": {
                "type": "string",
                "required": True,
                "nullable": True,
                "output": {},
            },
            "ext_cti": {
                "type": "string",
                "required": True,
                "nullable": True,
                "output": {},
            },
            "cnk_code": {
                "type": "string",
                "required": True,
                "nullable": True,
                "output": {},
            },
            "reference": {
                "type": "string",
                "required": True,
                "nullable": False,
                "output": {},
                "search": {"required": False, "operators": ["=", "ilike"]},
            },
            "vat": {
                "type": "float",
                "required": True,
                "nullable": False,
                "output": {},
            },
            "indicated_price": {
                "type": "float",
                "required": True,
                "nullable": False,
                "output": {},
            },
            "manufacturer": {
                "type": "string",
                "required": True,
                "nullable": True,
                "output": {},
            },
            "category": {
                "type": "string",
                "required": True,
                "nullable": False,
                "output": {},
            },
            "price_htva": {
                "type": "float",
                "required": True,
                "nullable": False,
                "output": {},
            },
            "price_tvac": {
                "type": "float",
                "required": True,
                "nullable": False,
                "output": {},
            },
        }
