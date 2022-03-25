# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component


class CartService(Component):

    _inherit = "sale.cart.service"

    @property
    def _json_address_parser(self):
        parser = super(CartService, self)._json_address_parser
        parser.append("vet_depot_number")
        parser.append("vet_subscription_number")
        return parser

    @property
    def _address_output_schema(self):
        schema = super(CartService, self)._address_output_schema
        schema.update(
            {
                "vet_depot_number": {
                    "type": "string",
                    "required": False,
                    "nullable": True,
                },
                "vet_subscription_number": {
                    "type": "string",
                    "required": False,
                    "nullable": True,
                },
            }
        )
        return schema
