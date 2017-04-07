# -*- coding: utf-8 -*-
# © 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Stock report for Alcyon',
    'version': '10.0.1.0.0',
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
        'delivery_rounds',
        'specific_purchase',
        'l10n_be_invoice_bba',
    ],
    'website': 'http://www.camptocamp.com',
    'data': [
        'views/report_template.xml',
        'views/report_deliveryslip.xml',
        'views/report_invoice.xml',
        'views/report_delivery_round.xml',
        'views/report_purchase_order.xml',
        'views/report_passport.xml',
        'data/paperformat.xml',
    ],
    'installable': True,
}
