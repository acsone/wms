# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class SaleOrder(models.Model):

    _inherit = "sale.order"

    @api.model
    def _parse_b2c_order(self, data, b2c_backend):
        res = super(SaleOrder, self)._parse_b2c_order(data, b2c_backend)
        res["discount_pricelist_id"] = b2c_backend.discount_pricelist_id.id
        return res
