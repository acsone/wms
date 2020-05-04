# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


from odoo import api, fields, models

from .utils import create_index


class StockPicking(models.Model):
    _inherit = "stock.picking"

    partner_id = fields.Many2one(index=True)
    group_id = fields.Many2one(index=True)

    @api.model_cr
    def init(self):

        # index for the default _order of stock.picking
        index_name = "stock_picking_order_list_sort_desc_index"
        create_index(
            self.env.cr, index_name, self._table, "(priority desc, date, id desc)"
        )
