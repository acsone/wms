# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component


class CartService(Component):

    _inherit = "sale.cart.service"

    def _prepare_cart(self):
        res = super(CartService, self)._prepare_cart()
        res["user_id"] = self.env.ref("alc_eshop_salesperson.eshop_salesperson").id
        return res
