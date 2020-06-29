# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.base_rest.components.service import to_int
from odoo.addons.component.core import Component
from odoo.osv.expression import AND


class ProductsService(Component):
    """
    Products services.

    Provides methods to get the products available for B2C
    """

    _inherit = "base.b2c.rest.service"
    _name = "products.service"
    _usage = "products"

    # api methods
    def search(self, **params):
        """
        Return the list of available products
        """
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
                fields=[
                    "name",
                    "default_code",
                    "barcode",
                    "create_date",
                    "immediately_usable_qty",
                    "list_price",
                    "cnk_code",
                ],
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
        product_schema = {
            "name": {"type": "string", "required": True, "nullable": False},
            "sku": {"type": "string", "required": True, "nullable": False},
            "eans": {
                "type": "list",
                "nullable": True,
                "schema": {"type": "string"},
                "required": False,
            },
            "cnk": {"type": "string", "required": True, "nullable": True},
            "price": {"type": "float", "required": True, "nullable": False},
            "create_date": {"type": "datetime", "required": True, "nullable": False},
            "quantity": {"type": "float", "required": True, "nullable": False},
        }
        schema = {
            "size": {"type": "integer"},
            "data": {
                "type": "list",
                "schema": {"type": "dict", "schema": product_schema},
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
        res = {
            "name": read_item["name"],
            "sku": read_item["default_code"],
            "cnk": read_item["cnk_code"] or None,
            "price": read_item["list_price"],
            "create_date": self._to_dt_utc_with_tz(read_item["create_date"]),
            "quantity": read_item["immediately_usable_qty"],
            "eans": [],
        }
        ean = read_item["barcode"]
        if ean:
            res["eans"] = [ean]
        return res
