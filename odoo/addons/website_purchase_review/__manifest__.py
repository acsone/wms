# -*- coding: utf-8 -*-
# © 2018 Okia SPRL <Sylvain Van Hoof>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Website purchase review',
    'version': '10.0.1.0.0',
    'author': 'Okia SPRL',
    'license': 'AGPL-3',
    'category': 'Others',
    'description': """
    Website purchase review
    """,
    'depends': [
        'purchase',
        'stock',
        'stock_orderpoint_product',
        'code_abc'
    ],
    'data': [
        "views/purchase_order.xml",
        "views/templates.xml"
    ],
    'website': 'http://www.camptocamp.com',
    'installable': True,
}
