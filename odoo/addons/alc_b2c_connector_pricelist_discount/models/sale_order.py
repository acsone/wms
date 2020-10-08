# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class SaleOrder(models.Model):

    _inherit = "sale.order"

    @api.model
    def _parse_b2c_order(self, data, b2c_backend):
        res = super(SaleOrder, self)._parse_b2c_order(data, b2c_backend)
        # ensure that discount_pricelist_id and supplier_promotion_allowed
        # are not filled from the partner
        res.update(
            {"discount_pricelist_id": False, "supplier_promotion_allowed": False}
        )
        return res
