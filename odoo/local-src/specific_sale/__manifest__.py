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
        'pricelist_discount',
        'sale',
        'sale_exception',
        'sale_product_additional',
        'stock_available_immediately',
    ],
    'website': 'http://www.camptocamp.com',
    'data': [
        # Data
        'data/exception_rule.xml',
        # Views
        'views/product_template.xml',
        'views/res_partner.xml',
        'views/sale.xml',
    ],
    'installable': True,
}
