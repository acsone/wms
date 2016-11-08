# -*- coding: utf-8 -*-
# © 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Specific sale for Alcyon',
    'version': '9.0.1.0.0',
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
