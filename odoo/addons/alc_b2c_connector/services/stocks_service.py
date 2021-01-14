# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.osv.expression import AND

from odoo.addons.base_rest.components.service import to_int
from odoo.addons.component.core import Component


class StocksService(Component):
    """
    Stocks services.

    Provides methods to get the product's stocks informations for B2C
    """

    _inherit = "base.b2c.rest.service"
    _name = "stocks.service"
    _usage = "stocks"

    # api methods
    def search(self, **params):
        domain = self.product_assortment_domain
        skus = params.get("skus")
        if skus:
            domain = AND([domain, [("default_code", "in", skus)]])
        limit = params.get("limit", None)
        offset = params.get("offset", 0)
        data = (
            self.env["product.product"]
            .suspend_security()
            .search_read(
                domain=domain,
                fields=["default_code", "immediately_usable_qty"],
                limit=limit,
                offset=offset,
            )
        )
        return self._to_search_result(data)

    def _validator_search(self):
        return {
            "skus": {
                "type": "list",
                "nullable": True,
                "required": False,
                "schema": {"type": "string"},
            },
            "limit": {"coerce": to_int, "nullable": True, "type": "integer"},
            "offset": {"coerce": to_int, "nullable": True, "type": "integer"},
        }

    def _validator_return_search(self):
        stock_schema = {
            "sku": {"type": "string", "required": True, "nullable": False},
            "quantity": {"type": "float", "required": True, "nullable": False},
        }
        schema = {
            "size": {"type": "integer"},
            "data": {
                "type": "list",
                "schema": {"type": "dict", "schema": stock_schema},
            },
        }
        return schema

    # private methods

    def _to_search_result(self, read_result):
        res = {
            "size": len(read_result),
            "data": [self._item_read_to_search_result(item) for item in read_result],
        }
        return res

    def _item_read_to_search_result(self, read_item):
        return {
            "sku": read_item["default_code"],
            "quantity": read_item["immediately_usable_qty"],
        }
