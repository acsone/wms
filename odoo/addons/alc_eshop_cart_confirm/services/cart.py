# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component


class CartService(Component):

    _inherit = "shopinvader.cart.service"

    def confirm(self):
        """Confirm cart. Topology is changed from cart to sale and the
        confirmation process is launched in background. This method
        will evolve or be replaced..."""
        cart = self._get()
        cart.action_confirm_cart()
        cart.action_confirm_background()
        return self._to_json(cart)

    def _validator_confirm(self):
        return {}

    # CODE TO MOVE: REQUIRED FOR A DEMO
    def search(self):
        """Return the cart that have been set in the session or
           search an existing cart for the current partner"""
        if not self.cart_id:
            # By default, shopinvader doesn't create a cart on a search
            # to avoir to be polluted by google calling search on
            # guest user... it's not the case for alcyon
            return self._to_json(self._get(create_if_not_found=True))
        return super(CartService, self).search()
