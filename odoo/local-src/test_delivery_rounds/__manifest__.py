# -*- coding: utf-8 -*-
# © 2019 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Tests delivery rounds',
    'version': '1.0',
    'author': "Alexandre Fayolle",
    'maintainer': 'Camptocamp',
    'category': 'Stock Management',
    'depends': [
        'delivery_rounds_alcyon',
        'delivery_rounds_refill',
        'product_additional',
        'stock_picking_zone',
        'stock_lot_loss',
        'stock_reassign_auto',
        'specific_sale',
        'specific_shipping_costs',
        'specific_account',
    ],
    'data': [
    ],
    'installable': True,
    'auto_install': False,
    'license': 'AGPL-3',
    'application': False,
}
