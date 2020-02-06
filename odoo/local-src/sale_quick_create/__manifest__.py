# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Sale Quick Create',
    'description': """
        Fast Sale Order Creation""",
    'version': '10.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'ACSONE SA/NV',
    'website': 'https://acsone.eu/',
    'depends': [
        "delivery",
        "sale",
        "sale_triple_discount",
        "sale_confirm_background",
        "specific_sale",
        "speedy_views",
        "web_readonly_bypass",
    ],
    'data': [
        'views/sale_order_line.xml',
        'views/sale_order.xml',
    ],
    'demo': [],
}
