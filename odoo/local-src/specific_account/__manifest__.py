# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Specific account for Alcyon',
    'version': '10.0.1.0.0',
    'author': 'Camptocamp',
    'license': 'AGPL-3',
    'category': 'Sales',
    'depends': [
        'sale',
        'specific_base',
        'pricelist_discount',
        # TODO: To migrate in V10
        # 'l10n_be_apb_tax',
        # 'l10n_be_antibiotic_tax',
        # 'l10n_be_invoice_bba',
        'report_intrastat',
        'account',
        'analytic',
        'account_cancel',
        'account_invoice_check_total',
    ],
    'website': 'http://www.camptocamp.com',
    'data': [
        # TODO: To migrate in V10
        # 'data/account_tax_group.xml',
        'views/account_invoice_view.xml',
        'views/res_config.xml',
        'views/ir_sequence.xml',
        'views/menu.xml',
        'views/account_analytic_tag.xml',
    ],
    'installable': True,
}
