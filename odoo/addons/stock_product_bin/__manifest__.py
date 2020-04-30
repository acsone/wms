# -*- coding: utf-8 -*-
# Copyright 2016-2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Stock Product Bin',
    'version': '1.0',
    'author': 'BCIM',
    'maintainer': 'Camptocamp',
    'category': 'Stock',
    'depends': [
        'stock',
        'stock_location_act_as_view',
    ],
    'data': [
        'views/product.xml',
        'views/stock.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'AGPL-3',
    'application': False,
}
