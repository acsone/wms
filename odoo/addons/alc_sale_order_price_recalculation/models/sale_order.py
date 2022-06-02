# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class SaleOrder(models.Model):

    _inherit = "sale.order"

    @api.model
    def _get_update_price_fields_and_values(self, in_memory_line):
        res = super(SaleOrder, self)._get_update_price_fields_and_values(in_memory_line)
        in_memory_line.onchange_product_id_reset_discount()
        res.update(
            {
                "discount2": in_memory_line.discount2,
                "discount3": in_memory_line.discount3,
            }
        )
        return res
