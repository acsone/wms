# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Specific sale for Alcyon',
    'version': '10.0.1.0.0',
    'author': 'Camptocamp',
    'license': 'AGPL-3',
    'category': 'Sales',
    'depends': [
        'delivery',
        'pricelist_discount',
        'sale',
        'sale_exception',
        'sales_team',
        'stock',
        'stock_available_immediately',
        'specific_data',
        'stock_lot_track',
        'sale_cancel_remaining',
    ],
    'website': 'http://www.camptocamp.com',
    'data': [
        # Data
        'data/base_override.yml',  # To remove all base exception rules
        'data/exception_rule.xml',
        # Report
        'report/sale_order.xml',
        # Views
        'views/product_template.xml',
        'views/res_partner.xml',
        'views/sale.xml',
        'views/sale_report.xml',
    ],
    'installable': True,
}
