# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from werkzeug.exceptions import NotFound

from odoo.addons.base_rest import restapi
from odoo.addons.component.core import Component


class CartService(Component):

    _inherit = "sale.cart.service"

    @restapi.method(
        [(["/confirm"], "POST")],
        input_param=restapi.CerberusValidator("_confirm_input_schema"),
        output_param=restapi.CerberusValidator("_cart_schema"),
    )
    def confirm(self, **params):
        """Confirm cart. Topology is changed from cart to sale and the
        confirmation process is launched in background. This method
        will evolve or be replaced..."""
        cart = self._find_open_cart(params.get("uuid", None))
        if not cart:
            raise NotFound("No cart found")
        upd_vals = self._prepare_cart_for_confirmation(cart, params)
        if upd_vals:
            cart.update(upd_vals)
        cart.action_confirm_cart()
        cart.action_confirm_background()
        return self._response_for_cart(cart)

    # #######
    # schemas
    # #######
    def _confirm_input_schema(self):
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

    # ##############
    # implementation
    # ##############
    def _confirm_params_to_upd_vals(self, cart, params):
        upd_vals = {}
        customer_ref = params.get("customer_ref")
        if customer_ref:
            upd_vals["client_order_ref"] = customer_ref
        note = params.get("note")
        if note:
            upd_vals["note"] = note
        return upd_vals

    def _prepare_cart_for_confirmation(self, cart, params):
        upd_vals = self._confirm_params_to_upd_vals(cart, params)
        if upd_vals:
            upd_vals.update(cart.play_onchanges(upd_vals, upd_vals.keys()))
        return upd_vals

    def _convert_cart_to_json(self, sale):
        json = super(CartService, self)._convert_cart_to_json(sale)
        json["customer_ref"] = sale.client_order_ref or None
        return json
