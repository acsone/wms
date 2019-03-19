# -*- coding: utf-8 -*-
# Copyright 2016-2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Stock Group by partner',
    'version': '1.0',
    'author': "BCIM",
    'maintainer': 'Camptocamp',
    'category': 'Stock Management',
    'depends': [
        'sale_stock',
        'stock_constraint',
        'delivery',
    ],
    'data': [
        'views/stock.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'AGPL-3',
    'application': False,
}
