# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models

from ..context import _updated_cart_line_ids_ctx


class SaleOrderLine(models.Model):

    _inherit = "sale.order.line"

    def _transactions_to_record_write(self, transactions):
        res = super(SaleOrderLine, self)._transactions_to_record_write(transactions)
        _updated_cart_line_ids_ctx.get().append(self.id)
        return res
