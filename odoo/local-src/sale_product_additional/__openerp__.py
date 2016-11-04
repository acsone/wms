# -*- coding: utf-8 -*-
# © 2016 Julien Coux (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Sale Product Additional',
    'version': '9.0.1.0.1',
    'author': 'Camptocamp',
    'license': 'AGPL-3',
    'category': 'Specific',
    'website': 'http://www.camptocamp.com',
    'images': [],
    'depends': [
        'base',
        'product',
        'sale',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/product_template.xml',
        'views/sale_order.xml',
    ],
    'test': [],
    'installable': True,
    'auto_install': False,
}
