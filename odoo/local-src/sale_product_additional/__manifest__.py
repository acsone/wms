# -*- coding: utf-8 -*-
# Copyright 2016 Julien Coux (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Sale Product Additional',
    'version': '10.0.1.0.0',
    'author': 'Camptocamp',
    'license': 'AGPL-3',
    'category': 'Specific',
    'website': 'http://www.camptocamp.com',
    'depends': [
        'base',
        'product',
        'sale',
        # Because when Odoo launch the tests on this module,
        # it has not yet loaded the `purchase` module,
        # the default `purchase_warn` value is not used,
        # so the test fail (on partner creation),
        # because we have a SQL constraint not null on this field,
        # but no default value.
        # To fix it, we add a dependence on `purchase` module.
        'purchase',  # Only to fix problem with unit tests
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/product_template.xml',
        'views/sale_order.xml',
    ],
    'installable': True,
    'auto_install': False,
}
