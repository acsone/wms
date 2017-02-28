
# -*- coding: utf-8 -*-
# Copyright 2016 Julien Coux (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Specific stock for Alcyon',
    'version': '9.0.1.0.0',
    'author': 'Camptocamp',
    'license': 'AGPL-3',
    'category': 'Warehouse',
    'depends': [
        'product',
        'product_expiry',
        'stock',
        'stock_production_lot_expired_dates',
    ],
    'website': 'http://www.camptocamp.com',
    'data': [
        'views/product_category.xml',
        'views/product_template.xml',
        'views/stock_pack_operation.xml',
    ],
    'installable': True,
}
