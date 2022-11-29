# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl

from odoo.addons.component.core import Component


class CartService(Component):

    _inherit = "sale.cart.service"

    def _convert_one_line(self, line):
        # Hack: see module manifest
        json = super(CartService, self)._convert_one_line(line)
        if line.product_id.is_human:
            json["qty_unavailable"] = 0
        return json
