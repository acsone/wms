# -*- coding: utf-8 -*-
# Copyright 2018 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Cash on delivery',
    'version': '10.0.1.0.0',
    'author': "BCIM",
    'category': 'Stock Management',
    'depends': [
        'sale_stock',
        'account',
    ],
    'data': [
        'views/account_payment_term.xml',
        'views/stock_picking.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'AGPL-3',
    'application': False,
}
