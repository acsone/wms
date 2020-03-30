# -*- coding: utf-8 -*-
# Copyright 2017-2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

{
    'name': 'Specific shipping costs for Alcyon',
    'version': '10.0.1.0.0',
    'author': 'Camptocamp',
    'license': 'AGPL-3',
    'category': 'Delivery',
    'depends': [
        'delivery',
        'delivery_rounds',
        'delivery_rounds_refill',
        'mrp',
        'specific_sale',
        'specific_stock',
        'specific_data',
    ],
    'website': 'http://www.camptocamp.com',
    'data': [
        'views/delivery_carrier.xml',
    ],
    'installable': True,
}
