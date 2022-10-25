# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.base_rest import restapi
from odoo.addons.base_rest.components.service import to_int
from odoo.addons.component.core import Component


def date_parser(date_str):
    return fields.Date.from_string(date_str) if date_str else None


class DiscountService(Component):

    _inherit = [
        "authenticated_partner.mixin",
        "standard.service.mixin",
        "paginated.service.mixin",
    ]
    _name = "supplier_discounts.service"
    _collection = "shopinvader.backend"
    _usage = "discounts"

    @property
    def model(self):
        return self.env["product.supplierinfo"]

    def _get_base_domain(self, keyword=None):  # for standard_service signature
        if not self.partner.supplier_promotion_sale_allowed:
            domain = [(0, "=", 1)]
        else:
            domain = self.partner._get_product_domain()
            domain[0] = ("product_tmpl_id." + domain[0][0], domain[0][1], domain[0][2])
            domain.append(("is_past", "=", False))
        return domain

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
        records = self._records(domain, **args)
        count = self.model.search_count(domain)
        return self._paginate_result(count, self._process_records(records, "output"))

    def _records(self, domain, page=1, per_page=10):
        offset = per_page * (page - 1) if per_page and page else 0
        return self.model.search(domain, limit=per_page, offset=offset)

    def _process_records(self, records, keyword):
        jsons = super(DiscountService, self)._process_records(records, keyword)
        for rec, data in zip(records, jsons):
            data["reference"] = rec.product_tmpl_id.default_code
        return jsons

    def _output_schema(self):
        return self._get_schema("output")

    def _search_input_schema(self):
        return self._get_schema("search", search=True)

    def _paginated_output_schema(self):
        return self._paginate_schema(self._get_schema("output"))

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
            "reference": {
                "type": "string",
                "required": True,
                "nullable": False,
                "output": {},
                "field": "product_tmpl_id.default_code",
                "search": {"required": False, "operators": ["=", "ilike"]},
            },
            "date_start": {
                "type": "date",
                "coerce": date_parser,
                "required": True,
                "nullable": False,
                "parser": "date_start",
                "output": {},
            },
            "date_end": {
                "type": "date",
                "coerce": date_parser,
                "required": True,
                "nullable": False,
                "parser": "date_end",
                "output": {},
            },
            "is_promotion": {
                "type": "boolean",
                "required": True,
                "nullable": False,
                "parser": "is_promotion",
                "output": {},
            },
            "is_sale_discount": {
                "type": "boolean",
                "required": True,
                "nullable": False,
                "parser": "is_sale_discount",
                "output": {},
            },
            "discount_sale": {
                "type": "float",
                "required": True,
                "nullable": False,
                "parser": "discount_sale",
                "output": {},
            },
            "ratio_main_product": {
                "type": "integer",
                "required": True,
                "nullable": False,
                "parser": "ratio_main_product",
                "output": {},
            },
            "ratio_promotional_product": {
                "type": "integer",
                "required": True,
                "nullable": False,
                "parser": "ratio_promotional_product",
                "output": {},
            },
        }
