# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductProduct(models.Model):

    _inherit = "product.product"

    stock_state = fields.Selection(
        selection_add=[("supplier_out_of_stock", "Supplier Out Of Stock")]
    )

    @api.multi
    def _get_qty_available(self):
        self.ensure_one()
        return self.immediately_usable_qty

    @api.multi
    @api.depends("immediately_usable_qty", "state_id")
    def _compute_stock_state(self):
        supplier_out_of_stock_state = self.env.ref("alc_product_state.product_state_h")
        res = super(ProductProduct, self)._compute_stock_state()
        for record in self:
            if (
                record.stock_state in ("resupplying", "out_of_stock")
                and record.state_id == supplier_out_of_stock_state
            ):
                record.stock_state = "supplier_out_of_stock"
        return res
