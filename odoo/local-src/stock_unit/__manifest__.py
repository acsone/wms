# -*- coding: utf-8 -*-
# Copyright 2018 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Stock Unit',
    'version': '1.0',
    'author': "BCIM",
    'category': 'Stock Management',
    'depends': [
        'stock',
        'delivery',  # not required but necessary for Travis as it adds a
                     # required weigth_uom_id field in DB
        ],
    'data': [
        'views/stock_config_settings.xml',
        'views/product_template.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'AGPL-3',
    'application': False,
}
