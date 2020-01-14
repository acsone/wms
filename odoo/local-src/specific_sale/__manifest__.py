# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Specific sale for Alcyon',
    'version': '10.0.1.1.0',
    'author': 'Camptocamp',
    'license': 'AGPL-3',
    'category': 'Sales',
    'depends': [
        'delivery',
        'pricelist_discount',
        'product_additional',
        'sale',
        'sale_exception',
        'alc_sale_product_expected_receipt_date',
        'sales_team',
        'stock',
        'stock_available_immediately',
        'sale_triple_discount',
        'specific_data',
        'specific_partner',
        'specific_stock',
        'stock_lot_track',
        'stock_lot_loss',
        'sale_cancel_remaining',
        'specific_purchase',
        'stock_picking_backorder',
        'stock_picking_assignment',
        'stock_product_bin',
        'stock_refill',
        'procurement_sale',
        'sale_consignment',
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
        'views/pricelist_pv2.xml',
        'views/res_partner.xml',
        'views/sale.xml',
        'views/sale_report.xml',
        # Security
        'security/ir.model.access.csv',
        'security/ir_ui_menu.xml',
    ],
    'demo': [
        'demo/exception_rule.xml',
    ],
    'installable': True,
}
