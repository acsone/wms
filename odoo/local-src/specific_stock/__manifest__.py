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
        'delivery_rounds',
        'product',
        'product_expiry',
        'purchase',
        'sale',
        'specific_helpdesk',
        'specific_purchase',
        'stock',
        'stock_available_immediately',
        'stock_production_lot_expired_dates',
        'stock_receive_lot',
        'stock_reception_priority',
    ],
    'website': 'http://www.camptocamp.com',
    'data': [
        # Views
        'views/product_category.xml',
        'views/product_template.xml',
        'views/res_partner.xml',
        'views/stock_backorder_reason.xml',
        'views/stock_location.xml',
        'views/stock_production_lot.xml',
        'views/stock_config_settings.xml',
        'views/stock_quant_package.xml',
        'wizards/stock_receive_lot.xml',

        # Wizards
        'wizards/stock_backorder_choice.xml',

        # Security
        'security/ir.model.access.csv',

        # Data
        'data/ir_cron.xml',
        'data/ir_config_parameter.xml',
    ],
    'installable': True,
}
