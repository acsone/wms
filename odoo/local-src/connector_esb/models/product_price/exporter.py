# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping
from ...components.mapper import two_digits_fractional, falsy2emptystring


class ProductPriceExportMapper(Component):
    _name = 'esb.product.price.mapper'
    _inherit = ['esb.export.mapper']
    _apply_on = 'product.product'

    @classmethod
    def _component_match(cls, work):
        return bool(work.timestamp and work.timestamp.kind == 'product.price')

    direct = [
        (falsy2emptystring('default_code'), 'Sku'),
        (two_digits_fractional('list_price'), 'Price'),
    ]

    @mapping
    def compute_pharmacy_price(self, record):
        price = record.sale_price_2_export
        return {'PharmacyPrice': '{0:.3f}'.format(price or 0)}

    @mapping
    def compute_msrp(self, record):
        price = 0
        if record.product_tmpl_id:
            price = record.product_tmpl_id.indicated_price
        if price:
            return {'Msrp': '{0:.2f}'.format(price)}


class ProductPriceCronExporter(Component):

    _name = 'esb.product.price.cron.exporter'
    _inherit = ['esb.cron.exporter', ]
    _usage = 'record.exporter.cron'
    _apply_on = 'product.product'

    @classmethod
    def _component_match(cls, work):
        return bool(work.timestamp and work.timestamp.kind == 'product.price')

    def get_items(self, export_since):
        self.update_saleprice_2()
        return super(ProductPriceCronExporter, self).get_items(export_since)

    def update_saleprice_2(self):
        products = self.env['product.product'].search(self.get_items_domain())
        for product in products:
            sale_price_2 = product.sale_price_2
            if product.sale_price_2_export != sale_price_2:
                product.write({'sale_price_2_export': sale_price_2})

    def get_items_domain(self):
        return [('active', '=', True)]
