# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Pricelist Discount',
    'version': '10.0.1.0.1',
    'author': 'Camptocamp',
    'license': 'AGPL-3',
    'category': 'Sales Management',
    'depends': [
        'product',
        'purchase',
        'sale',
        'sale_stock',
    ],
    'website': 'http://www.camptocamp.com',
    'data': [
        # Report
        'report/sale_order.xml',
        # Views
        'views/account_invoice.xml',
        'views/product_supplierinfo.xml',
        'views/purchase_order.xml',
        'views/res_partner.xml',
        'views/sale_order.xml'
    ],
    'installable': True,
}
