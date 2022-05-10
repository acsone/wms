# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from werkzeug.exceptions import NotFound

from odoo import _, fields
from odoo.exceptions import ValidationError

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
        if not cart.partner_id.eshop_ordering_allowed:
            raise ValidationError(_("You are no allowed to pass an order on the EShop"))
        upd_vals = self._prepare_cart_for_confirmation(cart, params)
        if upd_vals:
            cart.update(upd_vals)
        cart.action_confirm_cart()
        cart._notify_note()
        cart.action_confirm_background()
        return self._response_for_cart(cart)

    # #######
    # schemas
    # #######
    def _confirm_input_schema(self):
        res = {"uuid": {"type": "string", "required": False, "nullable": True}}
        res.update(self._info_input_schema())
        return res

    # ##############
    # implementation
    # ##############
    def _prepare_cart_for_confirmation(self, cart, params):
        upd_vals = self._info_params_to_vals(params)
        upd_vals["date_order"] = fields.Datetime.now()
        upd_vals.update(cart.play_onchanges(upd_vals, upd_vals.keys()))
        return upd_vals
