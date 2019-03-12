# -*- coding: utf-8 -*-
# © 2016 BCIM sprl (http://www.bcim.be)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Stock Orderpoint Product',
    'version': '1.0',
    'author': "BCIM",
    'maintainer': "QANSEE",
    'category': 'Stock Management',
    'website': 'http://www.bcim.be',
    'depends': [
        'stock',
    ],
    'data': [
        'views/product.xml',
        'views/stock.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'AGPL-3',
    'application': False,
}
