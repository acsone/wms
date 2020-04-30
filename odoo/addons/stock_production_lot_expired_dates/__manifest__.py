
# -*- coding: utf-8 -*-
# Copyright 2016 Julien Coux (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Stock production lot expired dates',
    'version': '10.0.1.0.0',
    'author': 'Camptocamp',
    'license': 'AGPL-3',
    'category': 'Warehouse',
    'depends': [
        'product_expiry',
        'stock',
    ],
    'website': 'http://www.camptocamp.com',
    'data': [
        'views/stock_config.xml',
    ],
    'installable': True,
}
