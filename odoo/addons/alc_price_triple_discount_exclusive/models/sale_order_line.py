# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def compute_supplier_promotion(self):
        res = super(SaleOrderLine, self).compute_supplier_promotion()
        for line in self.filtered("order_id.discount_pricelist_id"):
            pricelist = line.order_id.discount_pricelist_id
            rule_price_id = pricelist.get_product_price_rule(
                line.product_id, line.product_uom_qty, line.order_id.partner_id
            )
            if self.env["product.pricelist.item"].browse(rule_price_id[1]).exclusive:
                line.discount2 = 0
        return res
