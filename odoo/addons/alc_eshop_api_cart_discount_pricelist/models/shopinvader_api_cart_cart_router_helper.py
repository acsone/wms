# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import contextvars

from odoo import api

from odoo.addons.sale.models.sale_order_line import SaleOrderLine
from odoo.addons.shopinvader_api_cart.routers.cart import (
    ShopinvaderApiCartRouterHelper as ShopinvaderApiCartRouterHelperBase,
)
from odoo.addons.shopinvader_api_cart.schemas import CartTransaction

_updated_cart_line_ids_ctx = contextvars.ContextVar(
    "updated_cart_line_ids", default=None
)


class ShopinvaderApiCartRouterHelper(ShopinvaderApiCartRouterHelperBase):
    @api.model
    def _apply_transactions_on_existing_cart_line(
        self, cart_line: SaleOrderLine, transactions: list[CartTransaction]
    ):
        res = super()._apply_transactions_on_existing_cart_line(cart_line, transactions)
        _updated_cart_line_ids_ctx.get().append(cart_line.id)
        return res

    @api.model
    def _apply_transactions(self, cart, transactions: list[CartTransaction]):
        updated_line_ids = []
        ctx_token = _updated_cart_line_ids_ctx.set(updated_line_ids)
        try:
            res = super()._apply_transactions(cart, transactions)
            updated_line_ids = _updated_cart_line_ids_ctx.get()
            for line in cart.order_line.filtered(
                lambda l, ids=updated_line_ids: l.id in updated_line_ids
            ):
                line.onchange_product_id_reset_discount()
            return res
        finally:
            _updated_cart_line_ids_ctx.reset(ctx_token)
