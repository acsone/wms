# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component


class CartService(Component):

    _inherit = "sale.cart.service"

    def _cart_schema(self):
        schema = super(CartService, self)._cart_schema()
        schema["channel"] = {
            "type": "string",
            "required": True,
            "nullable": False,
        }
        return schema

    def _prepare_cart(self):
        vals = super(CartService, self)._prepare_cart()
        vals["sale_channel"] = "web"
        return vals

    def _convert_cart_to_json(self, sale):
        json = super(CartService, self)._convert_cart_to_json(sale)
        json["channel"] = sale.sale_channel or None
        return json
