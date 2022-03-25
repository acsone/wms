# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.base_rest import restapi
from odoo.addons.component.core import Component


class CartService(Component):

    _inherit = "sale.cart.service"

    @restapi.method(
        [(["/next_suite_name"], "GET")],
        output_param=restapi.CerberusValidator("_suite_name_schema"),
    )
    def get_next_suite_name(self):
        """This service return the next suite name to apply to the cart
        if the cart contains meds products"""
        cart = self._find_open_cart()
        value = None
        if cart:
            value = cart.suite_name or cart.get_next_suite_name(cart)
        return {"value": value}

    def _suite_name_schema(self):
        return {"value": {"type": "string", "required": True, "nullable": True}}

    def _cart_schema(self):
        schema = super(CartService, self)._cart_schema()
        schema["suite_name"] = {
            "type": "string",
            "required": False,
            "nullable": True,
        }
        return schema

    def _confirm_input_schema(self):
        schema = super(CartService, self)._confirm_input_schema()
        schema["suite_name"] = {
            "type": "string",
            "required": False,
            "nullable": True,
        }
        return schema

    def _convert_cart_to_json(self, sale):
        json = super(CartService, self)._convert_cart_to_json(sale)
        json["suite_name"] = sale.suite_name or None
        return json

    def _confirm_params_to_upd_vals(self, cart, params):
        upd_vals = super(CartService, self)._confirm_params_to_upd_vals(cart, params)
        suite_name = params.get("suite_name")
        if suite_name:
            upd_vals["suite_name"] = suite_name
        return upd_vals
