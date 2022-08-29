# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrderLine(models.Model):

    _inherit = "sale.order.line"

    def _prepare_order_line_procurement(self, group_id):
        self.ensure_one()
        vals = super(SaleOrderLine, self)._prepare_order_line_procurement(
            group_id=group_id
        )
        vals[
            "delivery_requires_other_lines"
        ] = self._check_delivery_requires_other_lines()
        return vals

    def _check_delivery_requires_other_lines(self):
        self.ensure_one()
        return self.order_id.do_not_deliver_if_alone
