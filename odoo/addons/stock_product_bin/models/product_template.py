# -*- coding: utf-8 -*-
# Copyright 2016-2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    stock_bin_ids = fields.One2many("product.stock.bin", "product_id", "Stock Bins")

    def _bin(self):
        self.ensure_one()

        order_list = ["bin", "parking", "reserve"]
        order = {key: i for i, key in enumerate(order_list)}
        if self.stock_bin_ids:
            bins = self.stock_bin_ids.mapped("bin_location_id")
            return sorted(bins, key=lambda rec: order.get(rec.kind, 99))[0]
        return self.env["stock.location"].browse()
