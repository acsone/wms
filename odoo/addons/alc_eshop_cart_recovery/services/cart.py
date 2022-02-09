# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component


class CartService(Component):

    _inherit = "shopinvader.cart.service"

    def search(self):
        """Return the cart that have been set in the session or
           search an existing cart for the current partner"""
        if not self.cart_id:
            # By default, shopinvader doesn't create a cart on a search
            # to avoid to be polluted by google calling search on
            # guest user... it's not the case for alcyon
            return self._to_json(self._get(create_if_not_found=True))
        return super(CartService, self).search()

    def _get(self, create_if_not_found=True):
        cart = self.env["sale.order"].browse()
        if not self.cart_id:
            domain = [
                ("shopinvader_backend_id", "=", self.shopinvader_backend.id),
                ("typology", "=", "cart"),
                ("state", "=", "draft"),
                ("partner_id", "=", self.partner.id),
            ]
            cart = self.env["sale.order"].search(domain, limit=1)
        if cart:
            return cart
        return super(CartService, self)._get(create_if_not_found=create_if_not_found)
