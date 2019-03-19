# -*- coding: utf-8 -*-
# © 2016-2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Stock Reception Priority',
    'version': '1.0',
    'author': "BCIM",
    'maintainer': 'Camptocamp',
    'category': 'Stock Management',
    'depends': [
        'stock',
        'stock_grn',
        'stock_picking_sequence',
        'stock_available_immediately',
        'delivery_rounds',
    ],
    'data': [
        'views/stock.xml',
        'data/data.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'AGPL-3',
    'application': False,
}
