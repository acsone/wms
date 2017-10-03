# -*- coding: utf-8 -*-
# Copyright 2017 Julien Coux (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Product additional for Alcyon',
    'version': '10.0.1.0.0',
    'author': 'Camptocamp',
    'license': 'AGPL-3',
    'category': 'Product',
    'depends': [
        'product',
        'sale'
    ],
    'website': 'http://www.camptocamp.com',
    'data': [
        # Views
        "views/product_template.xml",
        "views/product_supplierinfo.xml",
    ],
    'installable': True,
}
