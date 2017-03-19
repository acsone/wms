# -*- coding: utf-8 -*-
# © 2016 Sylvain Van Hoof
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Zetes integration for Alcyon',
    'version': '9.0.1.0.0',
    'author': 'Sylvain Van Hoof',
    'license': 'AGPL-3',
    'category': 'Others',
    'description': """
    Zetes integration for Alcyon
    """,
    'depends': [
            'stock',
    ],
    'data': [
        'views/res_users.xml',
        'views/stock_picking_type.xml',
    ],
    'website': 'http://www.camptocamp.com',
    'installable': True,
}
