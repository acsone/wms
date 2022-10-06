# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models

from ..context import _updated_cart_line_ids_ctx


class SaleOrder(models.Model):

    _inherit = "sale.order"

    def _apply_transactions(self, transactions):
        try:
            updated_line_ids = []
            ctx_token = _updated_cart_line_ids_ctx.set(updated_line_ids)
            res = super(SaleOrder, self)._apply_transactions(transactions)
            updated_line_ids = _updated_cart_line_ids_ctx.get()
            for line in self.order_line.filtered(
                lambda l, ids=updated_line_ids: l.id in updated_line_ids
            ):
                line.onchange_product_id_reset_discount()
            return res
        finally:
            _updated_cart_line_ids_ctx.reset(ctx_token)
