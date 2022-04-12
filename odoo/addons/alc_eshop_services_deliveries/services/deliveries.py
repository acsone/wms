# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.base_rest import restapi
from odoo.addons.base_rest.components.service import to_int
from odoo.addons.component.core import Component


class PickingsService(Component):

    _inherit = "authenticated_partner.mixin"
    _name = "pickings.service"
    _collection = "shopinvader.backend"
    _usage = "pickings"

    @restapi.method(
        [(["/"], "GET")],
        input_param=restapi.CerberusValidator("_search_input_schema"),
        output_param=restapi.CerberusValidator("_search_output_schema"),
    )
    def search(self, from_date=None, **params):
        domain = self._get_domain(from_date=from_date)
        records = self._search(domain, **params)
        return self._paginate_search_records(domain, records)

    def _search(self, domain=None, from_date=None, **params):
        limit = params.pop("limit", None)
        per_page = params.pop("per_page", None) or limit
        domain = domain or self._get_domain(from_date=from_date)
        return self._records(domain, per_page=per_page, **params)

    @restapi.method(
        [(["/canceled"], "GET")],
        input_param=restapi.CerberusValidator("_search_input_schema"),
        output_param=restapi.CerberusValidator("_search_output_schema"),
    )
    def search_canceled(self, from_date=None, **params):
        domain = self._get_domain(from_date=from_date, states=["cancel"])
        records = self._search_canceled(domain, from_date=from_date, **params)
        return self._paginate_search_records(domain, records)

    def _search_canceled(self, domain=None, from_date=None, **params):
        domain = domain or self._get_domain(from_date=from_date, states=["cancel"])
        return self._search(domain, from_date=from_date, **params)

    @restapi.method(
        [(["/done"], "GET")],
        input_param=restapi.CerberusValidator("_search_input_schema"),
        output_param=restapi.CerberusValidator("_search_output_schema"),
    )
    def search_done(self, from_date=None, **params):
        domain = self._get_domain(from_date=from_date, states=["done"])  # TODO
        records = self._search_done(domain, from_date=from_date, **params)
        return self._paginate_search_records(domain, records)

    def _search_done(self, domain=None, from_date=None, **params):
        domain = domain or self._get_domain(from_date=from_date, states=["done"])
        return self._search(domain=domain, from_date=from_date, **params)

    def _search_input_schema(self):
        return {
            "page": {
                "coerce": to_int,
                "nullable": True,
                "type": "integer",
                "default": 1,
            },
            "per_page": {
                "coerce": to_int,
                "nullable": True,
                "type": "integer",
                "default": None,
            },
            "limit": {
                "coerce": to_int,
                "nullable": True,
                "type": "integer",
                "default": None,
            },
            "from_date": {"type": "string", "required": False, "nullable": True},
        }

    def _get_model_schema(self):
        return {
            # "id": {"type": "integer", "required": True, "nullable": False},
            "name": {"type": "string", "required": True, "nullable": False},
            "move_lines": {
                "type": "list",
                "schema": {"type": "dict", "schema": self._get_model_line_schema()},
            },
        }

    def _get_model_line_schema(self):
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
    def model(self):
        return self.env["stock.picking"]

    def _get_domain(self, from_date=None, states=None):
        domain = [("partner_id", "=", self.partner.id), ("backorder_id", "!=", False)]
        if from_date:
            domain += [("create_date", ">=", from_date)]
        if states:
            domain += [("state", "in", states)]
        return domain

    def _get(self, _id):
        domain = self._get_domain() + [("id", "=", _id)]
        return self.model.search(domain)

    def _records(self, domain, page=1, per_page=10):
        offset = per_page * (page - 1) if per_page and page else 0
        return self.model.search(domain, limit=per_page, offset=offset)

    def _paginate_search_records(self, domain, records):
        total_count = self.model.search_count(domain)
        return {"size": total_count, "data": self._to_json(records)}

    def _paginate_search(self, domain, page=1, per_page=10):
        records = self._records(domain, page=page, per_page=per_page)
        return self._paginate_search_records(domain, records)

    def _get_parser(self):
        return [
            "name",
            ("move_lines", ["id", "name"]),
        ]

    def _to_json(self, records, parser=None):
        parser = parser or self._get_parser()
        return records.jsonify(parser)
