# -*- coding: utf-8 -*-
# © 2017 Jacques-Etienne Baudoux (BCIM)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Stock Receive Wizard',
    'version': '9.0.1.0.0',
    'author': 'BCIM',
    'maintainer': 'Camptocamp',
    'license': 'AGPL-3',
    'category': 'Stock Management',
    'depends': [
        'stock',
        'stock_expired',
    ],
    'data': [
        'wizards/stock.xml',
    ],
    'installable': True,
}
