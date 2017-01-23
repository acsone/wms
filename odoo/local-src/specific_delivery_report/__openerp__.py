# -*- coding: utf-8 -*-
# © 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Stock picking for Alcyon',
    'version': '9.0.1.0.0',
    'author': 'Camptocamp',
    'license': 'AGPL-3',
    'category': 'Sales',
    'depends': [
        'stock',
        'specific_base',
        'report',
        'specific_account'
    ],
    'website': 'http://www.camptocamp.com',
    'data': [
        'views/report_deliveryslip.xml',
        'data/paperformat.xml',
    ],
    'installable': True,
}
