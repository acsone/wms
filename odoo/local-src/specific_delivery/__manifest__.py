# -*- coding: utf-8 -*-
# Copyright 2017 Julien Coux (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Specific delivery for Alcyon',
    'version': '10.0.1.0.0',
    'author': 'Camptocamp',
    'license': 'AGPL-3',
    'category': 'Delivery',
    'depends': [
        'delivery',
        'delivery_rounds',
    ],
    'website': 'http://www.camptocamp.com',
    'data': [
        # Views
        'views/delivery_carrier.xml',
        'views/sale_order.xml',
    ],
    'installable': True,
}
