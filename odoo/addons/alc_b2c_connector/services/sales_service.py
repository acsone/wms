# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _
from odoo.addons.base_rest.components.service import to_int
from odoo.addons.component.core import Component
from odoo.exceptions import MissingError


class SalesService(Component):
    """
    Stocks services.

    Provides methods to create and manage sale orders for B2C.

    date and confirmation date info are datetime formatted into ISO-8601
    with TZ info
    """

    _inherit = "base.b2c.rest.service"
    _name = "sales.service"
    _usage = "sales"

    # api methods
    def create(self, **params):
        """
        Create a sale order
        """
        so = (
            self.env["sale.order"]
            .suspend_security()
            ._create_from_chonovet(params, self.b2c_backend)
        )
        return {
            "id": int(so.b2c_ref),
            "ref": so.name,
            "state": so.state,
            "confirmation_date": self._to_dt_utc_with_tz(so.confirmation_date),
        }

    def get(self, _id):
        """
        Get order info
        """
        res = (
            self.env["sale.order"]
            .suspend_security()
            .search_read(domain=[("b2c_ref", "=", _id)], fields=self._read_fields)
        )
        if not res:
            raise MissingError(_("Sale order not found for chonovet id %s") % _id)
        return self._item_read_to_search_result(res[0])

    def search(self, **params):
        """
        Get orders info
        """
        domain = []
        ids = params.get("ids")
        if ids:
            domain.append(("b2c_ref", "in", ids))
        limit = params.get("limit", None)
        offset = params.get("offset", 0)
        data = (
            self.env["sale.order"]
            .suspend_security()
            .search_read(
                domain=domain, fields=self._read_fields, limit=limit, offset=offset
            )
        )
        return self._to_search_result(data)

    def _validator_create(self):
        return {
            "id": {"type": "integer", "nullable": False, "required": True},
            "customer_ref": {"type": "string", "nullable": False, "required": True},
            "date": {"type": "string", "nullable": False, "required": True},
            "recipient": {
                "type": "dict",
                "schema": {
                    "id": {"type": "string", "nullable": False, "required": True},
                    "title": {
                        "type": "string",
                        "nullable": False,
                        "required": False,
                        "allowed": ["mr", "mm"],
                    },
                    "first_name": {
                        "type": "string",
                        "nullable": False,
                        "required": True,
                    },
                    "last_name": {
                        "type": "string",
                        "nullable": False,
                        "required": True,
                    },
                    "street": {"type": "string", "nullable": True, "required": False},
                    "street2": {"type": "string", "nullable": True, "required": False},
                    "zip": {"type": "string", "nullable": True, "required": False},
                    "city": {"type": "string", "nullable": True, "required": False},
                    "email": {"type": "string", "nullable": False, "required": True},
                    "phone": {"type": "string", "nullable": True, "required": False},
                    "mobile": {"type": "string", "nullable": True, "required": False},
                },
            },
            "lines": {
                "type": "list",
                "nullable": False,
                "required": True,
                "schema": {
                    "type": "dict",
                    "schema": {
                        "line_id": {
                            "type": "integer",
                            "nullable": False,
                            "required": False,
                        },
                        "sku": {"type": "string", "required": True, "nullable": False},
                        "quantity": {
                            "type": "integer",
                            "required": True,
                            "nullable": False,
                            "coerce": to_int,
                        },
                    },
                },
            },
        }

    def _validator_return_create(self):
        return self._sale_info_schema

    def _validator_return_get(self):
        return self._sale_info_schema

    def _validator_search(self):
        return {
            "ids": {
                "type": "list",
                "nullable": True,
                "required": False,
                "schema": {"type": "integer"},
            },
            "limit": {"coerce": to_int, "nullable": True, "type": "integer"},
            "offset": {"coerce": to_int, "nullable": True, "type": "integer"},
        }

    def _validator_return_search(self):
        schema = {
            "size": {"type": "integer"},
            "data": {
                "type": "list",
                "schema": {"type": "dict", "schema": self._sale_info_schema},
            },
        }
        return schema

    # private methods
    @property
    def _read_fields(self):
        return ["b2c_ref", "state", "confirmation_date", "name"]

    @property
    def _sale_info_schema(self):
        return {
            "id": {"type": "integer", "required": True, "nullable": False},
            "ref": {"type": "string", "required": True, "nullable": False},
            "state": {"type": "string", "required": True, "nullable": False},
            "confirmation_date": {"type": "string", "required": True, "nullable": True},
        }

    def _to_search_result(self, read_result):
        res = {
            "size": len(read_result),
            "data": [self._item_read_to_search_result(item) for item in read_result],
        }
        return res

    def _item_read_to_search_result(self, read_item):
        return {
            "id": int(read_item["b2c_ref"]),
            "ref": read_item["name"],
            "state": read_item["state"],
            "confirmation_date": self._to_dt_utc_with_tz(
                read_item["confirmation_date"]
            ),
        }
