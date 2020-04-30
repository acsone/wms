# -*- coding: utf-8 -*-
# © 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Account Belgium BBA Fix',
    'version': '1.0',
    'category': 'Accounting & Finance',
    'license': 'AGPL-3',
    'author': "BCIM",
    'depends': [
        'l10n_be_invoice_bba',
    ],
    'data': [
        'views/account_invoice.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
