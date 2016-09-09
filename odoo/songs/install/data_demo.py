# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from pkg_resources import resource_stream

import anthem
from anthem.lyrics.loaders import load_csv_stream
from ..common import req


@anthem.log
def import_suppliers(ctx):
    """ Importing suppliers from csv """
    content = resource_stream(req, 'data/demo/supplier.csv')
    load_csv_stream(ctx, 'res.partner', content, delimiter=',')


@anthem.log
def import_clients(ctx):
    """ Importing clients from csv"""
    content = resource_stream(req, 'data/demo/customer.csv')
    load_csv_stream(ctx, 'res.partner', content, delimiter=',')


@anthem.log
def import_locators(ctx):
    """ Importing locators from csv"""
    content = resource_stream(req, 'data/demo/locators_subset.csv')
    load_csv_stream(ctx, 'stock.location', content, delimiter=',')


@anthem.log
def import_output_locations(ctx):
    """ Importing output locations from csv"""
    content = resource_stream(req, 'data/demo/chariots.csv')
    load_csv_stream(ctx, 'stock.location', content, delimiter=',')


@anthem.log
def import_products(ctx):
    """ Importing products from csv"""
    content = resource_stream(req, 'data/demo/product.csv')
    load_csv_stream(ctx, 'product.product', content, delimiter=',')
    ctx.env.cr.execute("""
        UPDATE product_template
        SET active=False
        WHERE id IN (SELECT product_tmpl_id
                     FROM product_product
                     WHERE not active)
    """)


@anthem.log
def import_product_supplierinfo(ctx):
    """ Importing product supplier infos from csv"""
    content = resource_stream(req, 'data/demo/product.csv')
    load_csv_stream(ctx, 'product.product', content, delimiter=',')
    ctx.env.cr.execute("""
        UPDATE product_template
        SET active = false
        WHERE id IN (SELECT product_tmpl_id
                     FROM product_product
                     WHERE active = false)
    """)


@anthem.log
def import_pricelists(ctx):
    """ Importing pricelists from csv"""
    content = resource_stream(req, 'data/demo/product.pricelist.csv')
    load_csv_stream(ctx, 'product.pricelist', content, delimiter=',')


@anthem.log
def main(ctx):
    """ Loading demo data """
    import_suppliers(ctx)
    import_clients(ctx)
    import_locators(ctx)
    import_output_locations(ctx)
    import_products(ctx)
    import_product_supplierinfo(ctx)
    import_pricelists(ctx)
