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
        ('price_unit', 'price'),
        ('price_total', 'price_inc_tax'),
        (falsy2zero('product_qty_canceled'), 'qty_cancelled'),
        (falsy2zero('product_qty_unavailable'), 'qty_backorder')
    ]

    @mapping
    def compute_sku(self, record):
        return {'sku': record.product_id.default_code or ''}

    @mapping
    def compute_price_inc_tax(self, record):
        unit_tax = record.price_reduce_taxinc - record.price_reduce
        unit_price_with_tax = record.price_unit + unit_tax
        return {'price_inc_tax': unit_price_with_tax}
