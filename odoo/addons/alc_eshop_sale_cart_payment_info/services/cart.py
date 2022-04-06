# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component


class CartService(Component):

    _inherit = "sale.cart.service"

    def _cart_schema(self):
        schema = super(CartService, self)._cart_schema()
        schema["payment"] = {
            "type": "dict",
            "schema": self._payment_output_schema,
            "required": False,
            "nullable": True,
        }
        return schema

    @property
    def _payment_output_schema(self):
        return {
            "mode": {
                "type": "dict",
                "schema": self._payment_mode_output_schema,
                "required": False,
                "nullable": True,
            }
        }

    @property
    def _payment_mode_output_schema(self):
        return {
            "id": {"type": "integer", "required": True, "nullable": False},
            "name": {"type": "string", "required": True, "nullable": False},
        }

    def _convert_cart_to_json(self, sale):
        json = super(CartService, self)._convert_cart_to_json(sale)
        json["payment"] = self._convert_payment_to_json(sale)
        return json

    def _convert_payment_to_json(self, sale):
        payment = {"mode": None}
        if sale.payment_mode_id:
            payment["mode"] = {
                "id": sale.payment_mode_id.id,
                "name": sale.payment_mode_id.name,
            }
        return payment
