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
