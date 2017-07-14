# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from pkg_resources import resource_stream

import anthem
from anthem.lyrics.loaders import load_csv_stream
from anthem.lyrics.records import create_or_update

from ..common import req


@anthem.log
def set_customer_lead_time(ctx):
    create_or_update(ctx, 'ir.values', '__setup__.product_customer_lead', {
        'key': 'default',
        'name': 'sale_delay',
        'model': 'product.template',
        'value_unpickle': '0',
    })


@anthem.log
def import_accounting_products(ctx):
    """ Importing accounting products """
    content = resource_stream(req, 'data/install/accounting_products.csv')
    load_csv_stream(ctx, 'product.product', content, delimiter=',')


@anthem.log
def main(ctx):
    """ Configuring products """
    set_customer_lead_time(ctx)
    import_accounting_products(ctx)
