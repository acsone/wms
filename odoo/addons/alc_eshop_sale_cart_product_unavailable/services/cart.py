# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl
from werkzeug.exceptions import NotFound

from odoo.addons.base_rest import restapi
from odoo.addons.component.core import Component


class CartService(Component):

    _inherit = "sale.cart.service"

    @restapi.method(
        [(["/refresh_qty_unavailable"], "POST")],
        input_param=restapi.CerberusValidator("_refresh_qty_unavailable_input_schema"),
        output_param=restapi.CerberusValidator(
            "_cart_with_qty_unavailable_diff_schema"
        ),
    )
    def refresh_qty_unavailable(self, **params):
        """ This service refresh the qty_unavailable info on the cart lines

        As result, a new field 'qty_unavailable_diff' is added into the line
        info. This field is filled with the delta qty of unavailable product
        before and after the recompute of unavailable product for the given line.
        The new qty is applied to the line and a new call to the method should
        will give 0 as qty_unavailable_diff if there is no diff between 2 calls
        """
        cart = self._find_open_cart(params.get("uuid", None))
        if not cart:
            raise NotFound("No cart found")
        updated_lines = cart.refresh_product_qties_unavailable()
        json = self._response_for_cart(cart)
        for line in json["lines"]:
            line["qty_unavailable_diff"] = updated_lines.get(line["id"], 0)
        return json

    def _refresh_qty_unavailable_input_schema(self):
        return {"uuid": {"type": "string", "required": False, "nullable": True}}

    def _cart_with_qty_unavailable_diff_schema(self):
        schema = self._cart_schema()
        schema["lines"]["schema"]["schema"]["qty_unavailable_diff"] = {
            "type": "float",
            "required": True,
            "nullable": False,
        }
        return schema

    @property
    def _line_output_schema(self):
        schema = super(CartService, self)._line_output_schema
        schema.update(
            {
                "qty_unavailable": {
                    "type": "float",
                    "required": True,
                    "nullable": False,
                },
            }
        )
        return schema

    def _convert_one_line(self, line):
        json = super(CartService, self)._convert_one_line(line)
        json["qty_unavailable"] = line.product_qty_unavailable or 0
        return json
