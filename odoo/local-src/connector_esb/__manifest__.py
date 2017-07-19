# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Specific ESB for Alcyon',
    'version': '10.0.1.0.0',
    'author': 'Camptocamp',
    'license': 'AGPL-3',
    'category': 'Connector',
    'depends': [
        'connector',
        'product',
        'sale',
        'purchase',
        'specific_partner',
        'specific_product',
        'specific_purchase',
        'sale_stock',
        'product_expiry',
        'product',
        'specific_purchase',
    ],
    'website': 'http://www.camptocamp.com',
    'data': [
        'data/install_lang.xml',
        'data/esb_backend.xml',
        'data/esb_backend_timestamp.xml',
        'data/ir_cron.xml',
        'views/esb_backend_views.xml',
        'views/account_tax_views.xml',
        'views/product_views.xml',
        'views/product_uom_views.xml',
        'views/product_state_views.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
}
