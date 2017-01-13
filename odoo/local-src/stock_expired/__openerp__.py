# -*- coding: utf-8 -*-
# © 2016 Julien Coux (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Stock expired',
    'version': '9.0.1.0.0',
    'author': 'Camptocamp',
    'license': 'AGPL-3',
    'category': 'Warehouse',
    'depends': [
        'mail',
        'product_expiry',
        'stock',
    ],
    'website': 'http://www.camptocamp.com',
    'data': [
        # Data
        'data/data.xml',
        # Views
        'views/stock_location.xml',
        'views/stock_quant.xml',
    ],
    'installable': True,
}
