
# -*- coding: utf-8 -*-
# © 2016 Julien Coux (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Stock production lot expired dates',
    'version': '9.0.1.0.0',
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
