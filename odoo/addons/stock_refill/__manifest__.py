# -*- coding: utf-8 -*-
# Copyright 2016-2017 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Stock Refill',
    'version': '1.0.1',
    'author': "BCIM",
    'maintainer': 'Camptocamp',
    'category': 'Stock Management',
    'depends': [
        'stock',
        'stock_quant_bylocation',
    ],
    'data': [
        'views/stock_location.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'AGPL-3',
    'application': False,
}
