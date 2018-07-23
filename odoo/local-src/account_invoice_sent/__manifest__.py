# -*- coding: utf-8 -*-
# Copyright 2016-2018 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Account Invoice Sent',
    'version': '1.0',
    'author': "BCIM",
    'license': 'AGPL-3',
    'category': 'Accounting & Finance',
    'depends': [
        'account',
    ],
    'data': [
        'views/account_invoice.xml',
        'views/res_partner.xml',
        'wizards/account_invoice_state_view.xml',
    ],
    'installable': True,
}
