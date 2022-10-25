# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.alc_cerberus_utils import utils
from odoo.addons.base_rest import restapi
from odoo.addons.base_rest.components.service import to_int
from odoo.addons.component.core import Component


def date_parser(date_str):
    return fields.Date.from_string(date_str) if date_str else None


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

    def _search(self, domain=None, from_date=None, canceled=False, **params):
        limit = params.pop("limit", None)
        per_page = params.pop("per_page", None) or limit
        domain = domain or self._get_domain(from_date=from_date)
        return self._records(domain, per_page=per_page, canceled=canceled)

    @restapi.method(
        [(["/canceled"], "GET")],
        input_param=restapi.CerberusValidator("_search_input_schema"),
        output_param=restapi.CerberusValidator("_search_output_schema"),
    )
    def search_canceled(self, from_date=None, **params):
        states = ["cancel"]
        domain = self._get_domain(from_date=from_date, states=states, canceled=True)
        records = self._search_canceled(domain, from_date=from_date, **params)
        # TODO: search count is wrong in this case because of the post search filtering
        # we should add a compute field, a special case in the count query,
        # or something like that. Maybe it will go away by itself at migration?
        return self._paginate_search_records(domain, records)

    def _search_canceled(self, domain=None, from_date=None, **params):
        domain = domain or self._get_domain(
            from_date=from_date, states=["cancel"], canceled=True
        )
        return self._search(domain, from_date=from_date, canceled=True, **params)

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
            "id": {"type": "integer", "required": True, "nullable": False},
            "date": {
                "type": "datetime",
                "required": True,
                "nullable": False,
                "coerce": utils.isoformat_str_dt_to_dt_utc,
            },
            "date_done": {
                "type": "datetime",
                "required": True,
                "nullable": True,
                "coerce": utils.isoformat_str_dt_to_dt_utc,
            },
            "name": {"type": "string", "required": True, "nullable": False},
            "move_lines": {
                "type": "list",
                "schema": {"type": "dict", "schema": self._get_model_line_schema()},
            },
            "partner": {"type": "dict", "schema": self._get_address_schema()},
        }

    def _get_model_line_schema(self):
        return {
            "name": {"type": "string", "required": True, "nullable": False},
            "qty_ordered": {"type": "float", "required": True, "nullable": False},
            "remaining_qty": {"type": "float", "required": True, "nullable": False},
            "state": {"type": "string", "required": True, "nullable": False},
            "reference": {"type": "string", "required": True, "nullable": False},
            "lots": {
                "type": "list",
                "schema": {"type": "dict", "schema": self._get_lot_schema()},
            },
            "serial_number": {"type": "string", "required": True, "nullable": True},
            "prix_brut_htva": {"type": "float", "required": True, "nullable": False},
            "prix_net_htva": {"type": "float", "required": True, "nullable": False},
        }

    def _get_lot_schema(self):
        return {
            "name": {"type": "string", "required": True, "nullable": False},
            "peremption": {
                "type": "date",
                "required": True,
                "nullable": False,
                "coerce": date_parser,
            },
        }

    def _get_address_schema(self):
        return {
            "name": {"type": "string", "required": True, "nullable": False},
            "street": {"type": "string", "required": True, "nullable": False},
            "city": {"type": "string", "required": True, "nullable": False},
            "country": {"type": "string", "required": True, "nullable": False},
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

    def _get_domain(self, from_date=None, states=None, canceled=False):
        lid = self.env.ref("stock.stock_location_customers").id
        domain = [
            # the final client should not be a B2C customer it should be the VT
            # that's why we search on the customer_id and not on the partner_id
            # which is the delivery address
            ("customer_id", "child_of", self.partner.id),
            ("location_dest_id", "=", lid),
        ]
        if from_date:
            date_key = "date_done" if states == ["done"] else "create_date"
            domain += [(date_key, ">=", from_date)]
        if states and not canceled:
            domain += [("state", "in", states)]
        return domain

    def _get(self, _id):
        domain = self._get_domain() + [("id", "=", _id)]
        return self.model.search(domain)

    def _records(self, domain, page=1, per_page=10, canceled=False):
        offset = per_page * (page - 1) if per_page and page else 0
        records = self.model.search(domain, limit=per_page, offset=offset)
        # of course, this violates the per_page argument.
        # to bypass this, we should use the trick to have the ORM transform the domain
        # and inject an additional where in the query.
        # for now this is only used in magento-api which does not put any limit,
        # so it's not worth the complexity
        # looking on move lines has the same problem with the per_page argument,
        # but also needs more complexity to filter on child_of picking_id.customer_id
        if canceled:
            key = "cancel"
            filter_r = lambda r: r.state == key or key in r.mapped("move_lines.state")
            records = records.filtered(filter_r)
        return records

    def _paginate_search_records(self, domain, records):
        total_count = self.model.search_count(domain)
        return {"size": total_count, "data": self._to_json(records)}

    def _paginate_search(self, domain, page=1, per_page=10):
        records = self._records(domain, page=page, per_page=per_page)
        return self._paginate_search_records(domain, records)

    def _get_parser(self):
        parser_partner = [
            "name",
            "email",
            "street:address",
            "city:locality",
            ("country_id", ["name"]),
        ]
        parser_lot = ["name:lot", "expiry_date:peremption"]
        parser_move_lines = [
            "name",
            "state",
            "product_qty:qty_ordered",
            "remaining_qty",
            ("reference", lambda ml, fn: ml.product_id.default_code),
            ("prix_net_htva", lambda ml, fn: ml.order_line_id.price_reduce),
            ("prix_brut_htva", lambda ml, fn: ml.order_line_id.price_unit),
            "serial_number",
            ("lot_ids:lots", parser_lot),
        ]
        return [
            "id",
            "name",
            "date",
            "date_done",
            ("partner_id", parser_partner),
            ("move_lines", parser_move_lines),
        ]

    def _to_json(self, records, parser=None):
        parser = parser or self._get_parser()
        return records.jsonify(parser)
