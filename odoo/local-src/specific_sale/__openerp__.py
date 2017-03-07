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
        'pricelist_discount',
        'sale',
        'sale_exception',
        'sale_product_additional',
        'stock_available_immediately',
    ],
    'website': 'http://www.camptocamp.com',
    'data': [
        'data/sale_exception.xml',
        'views/product_template.xml',
        'views/res_partner.xml',
        'views/sale.xml',
    ],
    'installable': True,
}
