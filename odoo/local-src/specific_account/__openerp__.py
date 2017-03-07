# -*- coding: utf-8 -*-
# © 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Specific account for Alcyon',
    'version': '9.0.1.0.0',
    'author': 'Camptocamp',
    'license': 'AGPL-3',
    'category': 'Sales',
    'depends': [
        'sale',
        'specific_base',
        'pricelist_discount',
        'l10n_be_apb_tax',
        'l10n_be_antibiotic_tax',
        'l10n_be_invoice_bba',
        'report_intrastat',
        'account',
        'analytic',
    ],
    'website': 'http://www.camptocamp.com',
    'data': [
        'data/account_tax_group.xml',
        'views/account_invoice_view.xml',
        'views/ir_sequence.xml',
        'views/menu.xml',
        'views/account_analytic_tag.xml',
    ],
    'installable': True,
}
