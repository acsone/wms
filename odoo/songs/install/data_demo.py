# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from pkg_resources import Requirement, resource_stream

import anthem
from anthem.lyrics.loaders import load_csv_stream


@anthem.log
def import_suppliers(ctx, req):
    """ Importing suppliers from csv """
    content = resource_stream(req, 'data/setup/suppliers.csv')
    load_csv_stream(ctx, 'res.partner', content, delimiter=',')


@anthem.log
def import_clients(ctx, req):
    """ Importing clients from csv"""
    content = resource_stream(req, 'data/setup/clients.csv')
    load_csv_stream(ctx, 'res.partner', content, delimiter=',')


@anthem.log
def import_locators(ctx, req):
    """ Importing locators from csv"""
    content = resource_stream(req, 'data/setup/locators_subset.csv')
    load_csv_stream(ctx, 'stock.location', content, delimiter=',')


@anthem.log
def import_output_locations(ctx, req):
    """ Importing output locations from csv"""
    content = resource_stream(req, 'data/setup/chariots.csv')
    load_csv_stream(ctx, 'stock.location', content, delimiter=',')


@anthem.log
def import_price_categories(ctx, req):
    """ Importing prices categories from csv"""
    content = resource_stream(req, 'data/setup/product.price.category.csv')
    load_csv_stream(ctx, 'product.price.category', content, delimiter=',')


@anthem.log
def import_product_templates(ctx, req):
    """ Importing product templates from csv"""
    content = resource_stream(req, 'data/setup/product.template.csv')
    load_csv_stream(ctx, 'product.template', content, delimiter=',')


@anthem.log
def import_products(ctx, req):
    """ Importing products from csv"""
    content = resource_stream(req, 'data/setup/products.csv')
    load_csv_stream(ctx, 'product.product', content, delimiter=';')


@anthem.log
def import_pricelists(ctx, req):
    """ Importing pricelists from csv"""
    content = resource_stream(req, 'data/setup/product.pricelist.csv')
    load_csv_stream(ctx, 'product.pricelist', content, delimiter=',')


@anthem.log
def main(ctx):
    """ Loading demo data """
    req = Requirement.parse('alcyon-odoo')

    import_suppliers(ctx, req)
    import_clients(ctx, req)
    import_locators(ctx, req)
    import_output_locations(ctx, req)
    import_price_categories(ctx, req)
    import_product_templates(ctx, req)
    import_products(ctx, req)
    import_pricelists(ctx, req)
