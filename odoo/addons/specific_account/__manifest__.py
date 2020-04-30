# -*- coding: utf-8 -*-
# Copyright 2016-2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Specific account for Alcyon',
    'version': '10.0.1.0.0',
    'author': 'Camptocamp',
    'license': 'AGPL-3',
    'category': 'Sales',
    'depends': [
        'sale',
        'purchase',
        'specific_base',
        'specific_purchase',
        'pricelist_discount',
        'l10n_be_apb_tax',
        'l10n_be_antibiotic_tax',
        'l10n_be_invoice_bba',
        'report_intrastat',
        'account',
        'account_cutoff_base',
        'analytic',
        'account_cancel',
        'account_invoice_check_total',
        'specific_shipping_costs',
        'product_analytic',
        'account_invoice_sent',
        'queue_job',
        # OCA/web
        'web_readonly_bypass',
    ],
    'website': 'http://www.camptocamp.com',
    'data': [
        # Data
        'data/account_tax_group.xml',
        'data/cron.xml',
        # Views
        'views/assets.xml',
        'views/account_analytic_tag.xml',
        'views/account_cutoff.xml',
        'views/account_invoice_report.xml',
        'views/account_invoice_view.xml',
        'views/account_move_line.xml',
        'views/menu.xml',
        'views/res_config.xml',
        'views/res_partner.xml',
        'views/sale_order.xml',
        'views/stock_picking_type_views.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
}
