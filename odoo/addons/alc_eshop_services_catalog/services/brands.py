# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from werkzeug.exceptions import NotFound

from odoo.addons.base_rest import restapi
from odoo.addons.component.core import Component


class BrandsService(Component):
    _inherit = ["standard.service.mixin", "paginated.service.mixin"]
    _name = "brands.service"
    _collection = "shopinvader.backend"
    _usage = "brands"

    @property
    def model(self):
        return self.env["product.brand"]

    @restapi.method(
        [(["/<int:_id>"], "GET")],
        input_param=restapi.CerberusValidator({}),
        output_param=restapi.CerberusValidator("_output_schema"),
    )
    def get(self, _id):
        brand = self.model.browse(_id)
        if not brand.exists():
            raise NotFound("No brand with this _id.")
        return self._process_records(brand, "output")[0]

    @restapi.method(
        [(["/"], "GET")],
        input_param=restapi.CerberusValidator("_search_input_schema"),
        output_param=restapi.CerberusValidator("_paginated_output_schema"),
    )
    def search(self, page=1, per_page=10, **params):
        vals = self._process_params(params, "search")
        domain = self._get_domain("search", vals)
        count, records = self._paginated_search(domain, page, per_page)
        return self._paginate_result(count, self._process_records(records, "output"))

    def _output_schema(self):
        return self._get_schema("output")

    def _search_input_schema(self):
        return self._get_schema("search", search=True)

    def _paginated_output_schema(self):
        return self._paginate_schema(self._get_schema("output"))

    def _get_schema_generator(self):
        return {
            "id": {
                "type": "integer",
                "required": True,
                "nullable": False,
                "parser": "id",
                "output": {},
            },
            "name": {
                "type": "string",
                "required": True,
                "nullable": False,
                "parser": "name",
                "output": {},
                "search": {"required": False, "operators": ["=", "ilike"]},
            },
        }
