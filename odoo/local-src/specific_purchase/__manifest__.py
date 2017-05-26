# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Specific purchase for Alcyon',
    'version': '10.0.1.0.0',
    'author': 'Camptocamp',
    'license': 'AGPL-3',
    'category': 'Sales',
    'depends': [
        'purchase',
        'stock',
        'calendar',
    ],
    'website': 'http://www.camptocamp.com',
    'data': [
        # Views
        "views/res_partner.xml",
        "views/product_template.xml",
        "views/purchase_order.xml",
        "views/bank_holiday.xml",
        "views/purchase_config_settings.xml",

        # Data
        "data/product_state.xml",
        "data/ir_config_parameter.xml",

        # Security
        "security/ir.model.access.csv",
    ],
    'installable': True,
}
