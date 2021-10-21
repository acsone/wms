# -*- coding: utf-8 -*-
# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


from odoo import api, fields, models

from .utils import create_index


class StockQuant(models.Model):
    _inherit = "stock.quant"

    negative_move_id = fields.Many2one(index=True)

    @api.model_cr
    def init(self):
        # index for incoming and ongoing move in product qty compute
        index_name = "stock_quant_product_id_qty_in_loc_idx"
        create_index(
            self.env.cr,
            index_name,
            self._table,
            "(product_id) include (id, product_id, qty, location_id)",
        )
