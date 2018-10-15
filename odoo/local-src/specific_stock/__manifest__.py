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
        'specific_data',
        'specific_helpdesk',
        'specific_purchase',
        'stock',
        'stock_available_immediately',
        'stock_expired',
        'stock_inventory_products',
        'stock_mts_mto_rule',
        'stock_operation_recompute',
        'stock_picking_assignment',
        'stock_picking_backorder',
        'stock_picking_zone',
        'stock_product_bin',
        'stock_production_lot_expired_dates',
        'stock_receive_lot',
        'stock_reception_priority',
        'mrp',
    ],
    'website': 'http://www.camptocamp.com',
    'data': [
        # Views
        'views/product_category.xml',
        'views/product_template.xml',
        'views/res_partner.xml',
        'views/stock_location.xml',
        'views/stock_production_lot.xml',
        'views/stock_config_settings.xml',
        'views/stock_quant_package.xml',
        'views/stock_move.xml',
        'views/reception_pharmacy.xml',

        # Wizards
        'wizards/stock_receive_lot.xml',
        'wizards/put_in_pack_helper.xml',
        'wizards/generate_voice_identifier.xml',

        # Views (loaded after wizards)
        'views/stock_picking.xml',

        # Security
        'security/ir.model.access.csv',
        'security/ir_ui_menu.xml',

        # Data
        'data/ir_cron.xml',
        'data/ir_config_parameter.xml',
        'data/product.category.csv',
        'data/ir_sequence.xml',
        'data/product.xml',
    ],
    'installable': True,
}
