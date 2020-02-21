# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Alc Edi Connector',
    'description': """
        Alcyon EDI connector""",
    'version': '10.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'ACSONE SA/NV',
    'website': 'https://acsone.eu/',
    'depends': [
        'purchase_order_ubl',
        'purchase_order_approved',
        'alc_purchase_order_ubl',
    ],
    'data': [
        'views/res_partner.xml',
        'security/alc_edi_connector.xml',
        'views/alc_edi_connector.xml',
        'views/purchase_order.xml',
    ],
    'demo': ['demo/alc_edi_connector.xml'],
    'external_dependencies': {'python': ['paramiko']},
}
