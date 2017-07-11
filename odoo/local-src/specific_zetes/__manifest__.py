# -*- coding: utf-8 -*-
# © 2016 Sylvain Van Hoof
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Zetes integration for Alcyon',
    'version': '10.0.1.0.0',
    'author': 'Sylvain Van Hoof',
    'license': 'AGPL-3',
    'category': 'Others',
    'description': """
    Zetes integration for Alcyon
    """,
    'depends': [
        'stock',
        'specific_print',
        'specific_data',
    ],
    'data': [
        # Views
        'views/res_users.xml',
        'views/res_partner.xml',
        'views/stock_picking_type.xml',
        'views/zetes_logger.xml',

        # Security
        'security/ir.model.access.csv',
    ],
    'website': 'http://www.camptocamp.com',
    'installable': True,
}
