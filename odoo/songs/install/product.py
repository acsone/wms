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
def import_product_categories(ctx):
    """ Importing product.categories from csv"""

    load_ctx = ctx.env.context.copy()
    load_ctx.update({'defer_parent_store_computation': True})
    Category = ctx.env['product.category'].with_context(load_ctx)
    content = resource_stream(req, 'data/install/product.category.csv')
    load_csv_stream(ctx, Category, content, delimiter=',')

    with ctx.log(u"Compute parent_left, parent_right"):
        ctx.env['product.category']._parent_store_compute()


@anthem.log
def import_accounting_products(ctx):
    """ Importing accounting products """
    content = resource_stream(req, 'data/install/accounting_products.csv')
    load_csv_stream(ctx, 'product.product', content, delimiter=',')


@anthem.log
def main(ctx):
    """ Configuring products """
    set_customer_lead_time(ctx)
    import_product_categories(ctx)
    # TODO: To reactivate after migration v10
    # import_accounting_products(ctx)
