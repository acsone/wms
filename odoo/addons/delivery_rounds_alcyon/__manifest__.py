# -*- coding: utf-8 -*-
# © 2016-2018 Jacques-Etienne Baudoux (BCIM)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Delivery Rounds Alcyon',
    'version': '1.0',
    'author': "BCIM",
    'maintainer': 'Camptocamp',
    'category': 'Stock Management',
    'depends': [
        'delivery_rounds',
        'stock_picking_zone',
    ],
    'data': [
        'views/round_instance.xml',
        'views/css.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'AGPL-3',
    'application': False,
}
