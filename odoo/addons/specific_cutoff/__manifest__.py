# -*- coding: utf-8 -*-
# Copyright 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Specific Cutoff',
    'version': '1.0',
    'author': "BCIM",
    'maintainer': 'Camptocamp',
    'category': 'Accounting & Finance',
    'depends': [
        'account_invoice_accrual',
    ],
    'data': [
        'data/ir_cron.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'AGPL-3',
    'application': False,
}
