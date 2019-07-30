# -*- coding: utf-8 -*-
# Copyright 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# Copyright 2018 Okia SPRL <sylvain@okia.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Stock Lot Loss',
    'version': '10.0.1.0.0',
    'author': "BCIM",
    'category': 'Stock Management',
    'depends': [
        'stock',
        'stock_operation_recompute',
        'stock_reassign_auto',
        'purchase'  # Add only for unittests
    ],
    'data': [
        'data/ir.sequence.csv',
        'data/stock.location.csv',
        'data/stock.picking.type.csv',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'AGPL-3',
    'application': False,
}
