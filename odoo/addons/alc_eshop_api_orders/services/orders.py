# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.alc_cerberus_utils import utils
from odoo.addons.base_rest import restapi
from odoo.addons.base_rest.components.service import to_int
from odoo.addons.component.core import Component


class OrdersService(Component):

    _inherit = "authenticated_partner.mixin"
    _name = "orders.service"
    _collection = "shopinvader.backend"
    _usage = "orders"

    @restapi.method(
        [(["/"], "GET")],
        input_param=restapi.CerberusValidator("_search_input_schema"),
        output_param=restapi.CerberusValidator("_search_output_schema"),
    )
    def search(self, **params):
        domain = self._get_domain(**params)
        records = self._search(domain, **params)
        return self._paginate_search_records(domain, records)

    def _search(self, domain=None, **params):
        from_date = params.pop("from_date", None)
        limit = params.pop("limit", None)
        per_page = params.pop("per_page", None) or limit
        domain = domain or self._get_domain(from_date)
        return self._records(domain, per_page=per_page, **params)

    def _search_input_schema(self):
        return {
            "page": {
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
            "per_page": {
                "coerce": to_int,
                "nullable": True,
                "type": "integer",
                "default": None,
            },
            "from_date": {
                "type": "datetime",
                "required": False,
                "nullable": False,
                "coerce": utils.isoformat_str_dt_to_dt_utc,
            },
        }

    def _get_model_schema(self):
        return {
            "id": {"type": "integer", "required": True, "nullable": False},
            "name": {"type": "string", "required": True, "nullable": False},
            "customer_ref": {"type": "string", "required": False, "nullable": True},
            "state": {"type": "string", "required": True, "nullable": False},
            "state_label": {"type": "string", "required": True, "nullable": True},
            "amount_total": {"type": "float", "required": True, "nullable": False},
            "date_order": {
                "type": "datetime",
                "required": True,
                "nullable": False,
                "coerce": utils.isoformat_str_dt_to_dt_utc,
            },
            "lines": {
                "type": "list",
                "schema": {"type": "dict", "schema": self._get_model_line_schema()},
            },
        }

    def _get_model_line_schema(self):
        return {
            "line_id": {"type": "integer", "required": True, "nullable": False},
            "reference": {"type": "string", "required": True, "nullable": False},
            "price": {"type": "float", "required": True, "nullable": False},
            "qty_ordered": {"type": "float", "required": True, "nullable": False},
            "qty_delivered": {"type": "float", "required": True, "nullable": False},
            "qty_canceled": {"type": "float", "required": True, "nullable": False},
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
        return self.env["sale.order"]

    def _get_domain(self, from_date=None, **params):
        domain = [("partner_id", "=", self.partner.id), ("typology", "=", "sale")]
        if from_date:
            domain.append(("create_date", ">=", from_date))
        return domain

    def _get(self, _id):
        domain_base = self._get_domain()
        domain = domain_base + [("id", "=", _id)]
        return self.model.search(domain)

    def _records(self, domain, page=1, per_page=10, **params):
        offset = per_page * (page - 1) if per_page and page else 0
        return self.model.search(domain, limit=per_page, offset=offset)

    def _paginate_search_records(self, domain, records):
        total_count = self.model.search_count(domain)
        return {"size": total_count, "data": self._to_json(records)}

    def _paginate_search(self, domain, page=1, per_page=10):
        records = self._records(domain, page=page, per_page=per_page)
        return self._paginate_search_records(domain, records)

    def _get_parser(self):
        field = self.model._fields["shopinvader_state"]

        def state_label(r, fn):
            return field.convert_to_export(r.shopinvader_state, r) or None

        parser_lines = self._get_parser_lines()
        return [
            "id",
            "name",
            "date_order",
            "amount_total",
            "state",
            "client_order_ref:customer_ref",
            ("state_label", state_label),
            ("order_line:lines", parser_lines),
        ]

    def _get_parser_lines(self):
        return [
            "id:line_id",
            "price_reduce_taxexcl:price",
            "product_uom_qty:qty_ordered",
            "qty_delivered",
            "product_qty_canceled:qty_canceled",
            ("product_id", ["default_code:sku"]),
        ]

    def _to_json(self, records):
        records_json = records.jsonify(self._get_parser())
        for record_json in records_json:
            for line in record_json["lines"]:
                line["reference"] = line.pop("product_id")["sku"]
        return records_json
