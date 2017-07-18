# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component


class ProductStockWebserviceMessage(Component):

    _name = 'esb.webservice.message.product.stock'
    _inherit = ['esb.webservice.message.base']
    _apply_on = ['product.product']
    _usage = 'ws.message.product.stock'

    def get_message(self, product_skus):
        products = self.env['product.product'].search(
            [('default_code', 'in', product_skus)]
        )
        data = []
        for product in products:
            values = {
                'sku': product.default_code,
                'stock': product.qty_available,
                # TODO: need more info
                'erpStockCode': '',
            }
            data.append(values)
        return self._produce_xml(data, list_item_el='stockItem')
