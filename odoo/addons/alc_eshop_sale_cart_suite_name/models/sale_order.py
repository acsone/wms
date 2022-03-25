# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class SaleOrder(models.Model):

    _inherit = "sale.order"

    @api.model
    def get_next_suite_name(self, cart):
        for line in cart.order_line:
            if line.product_id.is_meds:
                return super(SaleOrder, self).get_next_suite_name(cart)
        return None
