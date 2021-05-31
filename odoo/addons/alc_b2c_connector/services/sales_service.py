# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, fields
from odoo.exceptions import MissingError
from odoo.osv import expression

from odoo.addons.base_rest.components.service import to_int
from odoo.addons.component.core import Component


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
    # pylint: disable=method-required-super
    def create(self, **params):
        """
        Create a sale order
        """
        so = (
            self.env["sale.order"]
            .suspend_security()
            ._create_from_b2c(params, self.b2c_backend)
        )
        return self._sale_order_to_search_result(so)

    def get(self, _id):
        """
        Get order info:

        Into the response:
         * the field state can have one of the following value:
           * draft: Quote received and created into our system
           * sale: Sale Order confirmed
           * cancel: Sale Order cancelled
           * delivery: Sale Order sent to the vet
        * When state is "delivery" delivery info are provided by the
        deliveries field

        """
        domain = self._get_base_search_domain()
        domain = expression.AND([domain, [("b2c_ref", "=", _id)]])
        res = self.env["sale.order"].suspend_security().search(domain)
        if not res:
            raise MissingError(_("Sale order not found for id %s") % _id)
        return self._sale_order_to_search_result(res[0])

    def search(self, **params):
        """
        Get orders info. More information on the response content is available
        on the 'get' method
        """
        domain = self._get_base_search_domain()
        ids = params.get("ids")
        if ids:
            domain = expression.AND([domain, [("b2c_ref", "in", ids)]])
        limit = params.get("limit", None)
        offset = params.get("offset", 0)
        data = (
            self.env["sale.order"]
            .suspend_security()
            .search(domain, limit=limit, offset=offset)
        )
        return self._to_search_result(data)

    def cancel(self, _id):
        """
        Cancel Sale Order.
        Cancelling a sale order is only possible until
        the preparation has started (i.e., the picking is printed)
        """

        so = self.env["sale.order"].suspend_security()._cancel_from_b2c(order_id=_id)
        if so.state == "cancel":
            return {
                "status": "OK",
                "message": "Order  %s cancelled from b2c api" % so.name,
            }
        return {
            "status": "KO",
            "message": "Cannot cancel so %s , being process already" % so.name,
        }

    def _validator_cancel(self):
        return {}

    def _validator_return_cancel(self):
        return {
            "status": {
                "type": "string",
                "nullable": False,
                "required": True,
                "allowed": ["OK", "KO"],
            },
            "message": {"type": "string", "nullable": True, "required": False},
        }

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
                    "country_code": {
                        "type": "string",
                        "nullable": True,
                        "allowed": self.env["res.country"]._get_codes(),
                    },
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

    def _get_base_search_domain(self):
        return [("sale_channel", "=", self.b2c_backend.sale_channel)]

    @property
    def _sale_info_schema(self):
        return {
            "id": {"type": "integer", "required": True, "nullable": False},
            "ref": {"type": "string", "required": True, "nullable": False},
            "state": {"type": "string", "required": True, "nullable": False},
            "confirmation_date": {
                "type": "datetime",
                "required": True,
                "nullable": True,
            },
            "deliveries": {
                "type": "list",
                "nullable": False,
                "required": False,
                "schema": {
                    "type": "dict",
                    "schema": {
                        "tracking_reference": {
                            "type": "string",
                            "nullable": True,
                            "required": False,
                        },
                        "delivery_date": {
                            "type": "string",
                            "nullable": True,
                            "required": False,
                        },
                        "carrier": {
                            "type": "string",
                            "nullable": True,
                            "required": False,
                        },
                    },
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
                        "qty_ordered": {
                            "type": "integer",
                            "required": True,
                            "nullable": False,
                            "coerce": to_int,
                        },
                        "qty_delivered": {
                            "type": "integer",
                            "required": True,
                            "nullable": False,
                            "coerce": to_int,
                        },
                        "qty_cancelled": {
                            "type": "integer",
                            "required": True,
                            "nullable": False,
                            "coerce": to_int,
                        },
                        "qty_returned": {
                            "type": "integer",
                            "required": True,
                            "nullable": False,
                            "coerce": to_int,
                        },
                        "qty_backorder": {
                            "type": "integer",
                            "required": True,
                            "nullable": False,
                            "coerce": to_int,
                        },
                    },
                },
            },
        }

    def _to_search_result(self, sale_orders):
        res = {
            "size": len(sale_orders),
            "data": [self._sale_order_to_search_result(item) for item in sale_orders],
        }
        return res

    def _sale_order_to_search_result(self, sale_order):
        state = sale_order.b2c_state
        res = {
            "id": int(sale_order.b2c_ref),
            "ref": sale_order.name,
            "state": state,
            "confirmation_date": self._to_dt_utc_with_tz(sale_order.confirmation_date),
            "lines": [
                self._line_to_search_result(line)
                for line in sale_order.order_line.filtered("b2c_ref")
            ],
        }
        if state == "delivery":
            res["deliveries"] = self._deliveries_to_search_result(sale_order)
        return res

    def _line_to_search_result(self, order_line):
        return {
            "line_id": int(order_line.b2c_ref),
            "sku": order_line.product_id.default_code,
            "qty_ordered": int(order_line.product_uom_qty),
            "qty_delivered": int(order_line.qty_delivered),
            "qty_cancelled": int(order_line.product_qty_canceled),
            "qty_returned": int(order_line.product_qty_returned),
            "qty_backorder": int(order_line.product_qty_backorder),
        }

    def _deliveries_to_search_result(self, sale_order):
        ships = sale_order.mapped("picking_ids").filtered(
            lambda p: p.picking_type_code == "outgoing"
        )
        res = []
        for ship in ships:
            res.append(
                {
                    "tracking_reference": ship.carrier_tracking_ref or "",
                    "delivery_date": self._get_delivery_date(ship),
                    "carrier": ship.carrier_id.name or "",
                }
            )
        return res

    def _get_delivery_date(self, picking):
        """
        Get the delivery date from given picking.
        As the delivery date doesn't exist in Odoo, we use the write_date
        when the state is 'done'.
        :param picking: stock.picking
        :return: str
        """
        delivery_date = ""
        if picking.state == "done":
            write_date = fields.Datetime.from_string(picking.write_date)
            delivery_date = fields.Date.to_string(
                fields.Datetime.context_timestamp(picking, write_date)
            )
        return delivery_date
