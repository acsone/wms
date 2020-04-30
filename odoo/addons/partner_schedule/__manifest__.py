# -*- coding: utf-8 -*-
# Copyright 2019 Iryna Vyshnevska (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Working Schedule',
    'version': '10.0.1.0.0',
    'maintainer': 'Camptocamp',
    'category': 'Other',
    'depends': [
        'sales_team',
    ],
    'data': [
        'views/res_partner.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'AGPL-3',
    'application': False,
}
