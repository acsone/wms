# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _

from odoo.addons.alc_eshop_api_products_on_order.exceptions import CancelOrderLineError


class NoBackOrderOnBlanketOrderError(CancelOrderLineError):
    def __init__(self, product_name, order_ref, env):
        self.env = env
        error_msg = _(
            "No back order allowed for product %(name)s in sale blanket order %(order_ref)s",
            name=product_name,
            order_ref=order_ref,
        )
        super().__init__(error_msg)
