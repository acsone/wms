# -*- coding: utf-8 -*-
# © 2016 Sylvain Van Hoof
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Refund invoice',
    'version': '0.1',
    'summary': 'Allows to create customer/supplier refunds',
    'sequence': 30,
    'description': """
    Allows to create customer/supplier refunds
    """,
    'category': 'Accounting',
    'depends': ['account', 'purchase'],
    'data': [
        'views/account_invoice.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
