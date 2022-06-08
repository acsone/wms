# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.base_rest import restapi
from odoo.addons.component.core import Component


class CartService(Component):

    _inherit = "sale.cart.service"

    @restapi.method(
        [(["/info"], "POST")],
        input_param=restapi.CerberusValidator("_info_input_schema"),
        output_param=restapi.CerberusValidator("_cart_schema"),
    )
    def update(self, **params):
        """Endpoint to update cart informational fields (reference, suite
        number).

        No update of parameters such as shipping, etc. that could modify
        the total amount or the processing of the cart
        """
        cart = self._find_open_cart(params.get("uuid")) or self._create_empty_cart()
        cart.write(self._info_params_to_vals(params))
        return self._response_for_cart(cart)

    def _info_input_schema(self):
        return {
            "uuid": {"type": "string", "required": False, "nullable": True},
            "customer_ref": {"type": "string", "required": False, "nullable": True},
            "note": {"type": "string", "required": False, "nullable": True},
        }

    def _cart_schema(self):
        schema = super(CartService, self)._cart_schema()
        schema["customer_ref"] = {
            "type": "string",
            "required": False,
            "nullable": True,
        }
        return schema

    def _convert_cart_to_json(self, sale):
        json = super(CartService, self)._convert_cart_to_json(sale)
        json["customer_ref"] = sale.client_order_ref or None
        return json

    def _info_params_to_vals(self, params):
        upd_vals = {}
        customer_ref = params.get("customer_ref")
        if customer_ref:
            upd_vals["client_order_ref"] = customer_ref
        note = params.get("note")
        if note:
            upd_vals["note"] = note
        return upd_vals
