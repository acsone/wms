# -*- coding: utf-8 -*-
# © 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Specific partner for Alcyon',
    'version': '9.0.1.0.0',
    'author': 'Camptocamp',
    'license': 'AGPL-3',
    'category': 'Sales',
    'depends': [
        'sale',
        'delivery_rounds',
    ],
    'website': 'http://www.camptocamp.com',
    'data': [
        'security/ir.model.access.csv',
        'views/res_partner.xml',
    ],
    'installable': True,
}
