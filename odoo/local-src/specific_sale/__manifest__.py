# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Specific sale for Alcyon',
    'version': '10.0.1.0.0',
    'author': 'Camptocamp',
    'license': 'AGPL-3',
    'category': 'Sales',
    'depends': [
        'sale',
        'sale_exception',
    ],
    'website': 'http://www.camptocamp.com',
    'data': [
        'data/sale_exception.xml',
        'views/sale.xml',
    ],
    'installable': True,
}
