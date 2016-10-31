# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem
from anthem.lyrics.records import create_or_update


@anthem.log
def create_product_categories(ctx):
    """ Creating product categories """
    categories = [('__init.product_categ_materiel', u'Matériel'),
                  ('__init.product_categ_ali', u'Aliments'),
                  ('__init.product_categ_medoc', u'Médicaments'),
                  ('__init.product_categ_frigo', u'Frigo'),
                  # ('__init.product_categ_congel', u'congel -12'),
                  ]
    for xmlid, name in categories:
        create_or_update(ctx, 'product.category', xmlid, {'name': name})


@anthem.log
def set_customer_lead_time(ctx):
    create_or_update(ctx, 'ir.values', '__init.product_customer_lead', {
        'key': 'default',
        'name': 'sale_delay',
        'model': 'product.template',
        'value_unpickle': '0',
    })


@anthem.log
def main(ctx):
    """ Configuring products """
    create_product_categories(ctx)
    set_customer_lead_time(ctx)
