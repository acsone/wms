# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


from odoo import api, fields, models

from .utils import create_index


class StockMove(models.Model):
    _inherit = "stock.move"

    procurement_id = fields.Many2one(index=True)
    split_from = fields.Many2one(index=True)
    origin_returned_move_id = fields.Many2one(index=True)
    inventory_id = fields.Many2one(index=True)

    @api.model_cr
    def init(self):
        # index for incoming and ongoing move in product qty compute
        index_name = "stock_move_wip_product_id_idx"
        create_index(
            self.env.cr,
            index_name,
            self._table,
            "(product_id) where state not in ('done','cancel','draft') or state is null",
        )
