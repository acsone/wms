# -*- coding: utf-8 -*-
# © 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Stock report for Alcyon',
    'version': '9.0.1.0.0',
    'author': 'Camptocamp',
    'license': 'AGPL-3',
    'category': 'Sales',
    'depends': [
        'stock',
        'specific_base',
        'report',
        'specific_account',
        'account',
        'sale',
    ],
    'website': 'http://www.camptocamp.com',
    'data': [
        'views/report_template.xml',
        'views/report_deliveryslip.xml',
        'views/report_invoice.xml',
        'views/report_delivery_round.xml',
        'data/paperformat.xml',
    ],
    'installable': True,
}
