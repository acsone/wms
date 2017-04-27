# -*- coding: utf-8 -*-
# Copyright 2017 Julien Coux (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Specific shipping costs for Alcyon',
    'version': '10.0.1.0.0',
    'author': 'Camptocamp',
    'license': 'AGPL-3',
    'category': 'Delivery',
    'depends': [
        'delivery',
        'sale',
        'sale_stock',
    ],
    'website': 'http://www.camptocamp.com',
    'data': [
        # Views
        'views/account_invoice.xml',
        'views/delivery_carrier.xml',
        'views/sale_order.xml',
    ],
    'installable': True,
}
