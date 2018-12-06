# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import models, fields


class StockMove(models.Model):
    _inherit = 'stock.move'

    order_line_id = fields.Many2one('sale.order.line',
                                    string='Order line',
                                    related='procurement_id.sale_line_id',
                                    store=True)

    order_id = fields.Many2one('sale.order', related='order_line_id.order_id')
