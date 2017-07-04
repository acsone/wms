# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Specific ESB for Alcyon',
    'version': '10.0.1.0.0',
    'author': 'Camptocamp',
    'license': 'AGPL-3',
    'category': 'Connector',
    'depends': [
        'connector',
        'product',
    ],
    'website': 'http://www.camptocamp.com',
    'data': [
        'data/esb_backend.xml',
        'data/esb_backend_timestamp.xml',
        'data/ir_cron.xml',
        'views/esb_backend_views.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
}
