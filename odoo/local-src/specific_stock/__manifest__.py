
# -*- coding: utf-8 -*-
# Copyright 2016 Julien Coux (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Specific stock for Alcyon',
    'version': '10.0.1.0.0',
    'author': 'Camptocamp',
    'license': 'AGPL-3',
    'category': 'Warehouse',
    'depends': [
        'product',
        'product_expiry',
        'stock',
        'stock_production_lot_expired_dates',
        'stock_reception_priority',
        'stock_receive_lot',
    ],
    'website': 'http://www.camptocamp.com',
    'data': [
        # Views
        'views/product_category.xml',
        'views/product_template.xml',
        'views/stock_location.xml',
        'views/stock_production_lot.xml',
        'views/stock_config_settings.xml',
        'wizards/stock_receive_lot.xml',

        # Data
        'data/ir_cron.xml',
        'data/ir_config_parameter.xml',
    ],
    'installable': True,
}
