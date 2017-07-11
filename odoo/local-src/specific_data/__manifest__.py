# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Specific datas for Alcyon',
    'version': '10.0.1.0.0',
    'author': 'Camptocamp',
    'license': 'AGPL-3',
    'category': 'Base',
    'depends': [
        'base',
        'product',
        'stock',
    ],
    'website': 'http://www.camptocamp.com',
    'data': [
        'data/res.partner.category.csv',
        'data/product.category.csv',
        'data/product.pricelist.csv'
    ],
    'post_init_hook': 'post_init_hook',
    'installable': True,
}
