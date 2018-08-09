# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping
from ...components.mapper import falsy2zero


class SaleOrderLineExportMapper(Component):
    _name = 'esb.sale.order.line.export.mapper'
    _inherit = ['esb.export.mapper']
    _apply_on = 'sale.order.line'

    direct = [
        ('sequence', 'line_number'),
        ('product_uom_qty', 'qty_ordered'),
        (falsy2zero('qty_delivered'), 'qty_delivered'),
        (falsy2zero('price_reduce_taxexcl'), 'price'),
        (falsy2zero('price_reduce_taxinc'), 'price_inc_tax'),
        (falsy2zero('product_qty_canceled'), 'qty_cancelled'),
        (falsy2zero('product_qty_unavailable'), 'qty_backorder')
    ]

    @mapping
    def compute_sku(self, record):
        return {'sku': record.product_id.default_code or ''}
