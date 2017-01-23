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
        'report_intrastat',
        'l10n_be_invoice_bba',
    ],
    'website': 'http://www.camptocamp.com',
    'data': [
        'data/paperformat.xml',
        'views/report_invoice.xml',
        'views/account_invoice_view.xml',
        'views/menu.xml',
    ],
    'installable': True,
}
