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
    load_ctx = ctx.env.context.copy()
    load_ctx.update({'tracking_disable': True})
    Partner = ctx.env['res.partner'].with_context(load_ctx)
    content = resource_stream(req, 'data/demo/supplier.csv')
    load_csv_stream(ctx, Partner, content, delimiter=',')


@anthem.log
def import_clients(ctx):
    """ Importing clients from csv"""
    content = resource_stream(req, 'data/demo/customer.csv')

    load_ctx = ctx.env.context.copy()
    load_ctx.update({'tracking_disable': True})
    Partner = ctx.env['res.partner'].with_context(load_ctx)
    load_csv_stream(ctx, Partner, content, delimiter=',')


@anthem.log
def import_locations(ctx):
    """ Importing locations from csv"""

    load_ctx = ctx.env.context.copy()
    load_ctx.update({'defer_parent_store_computation': 'manually'})
    Location = ctx.env['stock.location'].with_context(load_ctx)
    with ctx.log(u" Importing family locations from csv"):
        content = resource_stream(req, 'data/install/location_family.csv')
        load_csv_stream(ctx, Location, content, delimiter=',')
    with ctx.log(u"Importing warehouse locations"):
        content = resource_stream(req, 'data/demo/location.csv')
        load_csv_stream(ctx, Location, content, delimiter=',')
    with ctx.log(u"Importing reserve locations"):
        content = resource_stream(req, 'data/demo/locators_reserve.csv')
        load_csv_stream(ctx, Location, content, delimiter=',')
    with ctx.log(u"Importing parking locations"):
        content = resource_stream(req, 'data/demo/locators_parking.csv')
        load_csv_stream(ctx, Location, content, delimiter=',')
    with ctx.log(u"Importing output locations"):
        content = resource_stream(req, 'data/demo/chariots.csv')
        load_csv_stream(ctx, Location, content, delimiter=',')

    with ctx.log(u"Compute parent_left, parent_right"):
        ctx.env['stock.location']._parent_store_compute()


@anthem.log
def import_products(ctx):
    """ Importing products from csv"""
    load_ctx = ctx.env.context.copy()
    load_ctx.update({'tracking_disable': True})
    Product = ctx.env['product.product'].with_context(load_ctx)
    content = resource_stream(req, 'data/demo/product.csv')
    load_csv_stream(ctx, Product, content, delimiter=',')
    content = resource_stream(req, 'data/demo/logistics_product.csv')
    load_csv_stream(ctx, Product, content, delimiter=';')
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
    content = resource_stream(req, 'data/demo/supplierinfo.csv')
    load_csv_stream(ctx, 'product.supplierinfo', content, delimiter=',')


@anthem.log
def import_pricelist_items(ctx):
    """ Importing pricelists from csv"""
    content = resource_stream(req, 'data/demo/pricelist_items.csv')
    load_csv_stream(ctx, 'product.pricelist.item', content, delimiter=',')


@anthem.log
def import_delivery_round_config(ctx):
    """ Importing delivery round config from csv"""
    content = resource_stream(req, 'data/demo/delivery_vehicle.csv')
    load_csv_stream(ctx, 'round.vehicle', content, delimiter=',')
    content = resource_stream(req, 'data/demo/delivery_zone.csv')
    load_csv_stream(ctx, 'round.zone', content, delimiter=',')
    content = resource_stream(req, 'data/demo/delivery_clients.csv')
    load_csv_stream(ctx, 'round.zone.position', content, delimiter=',')


@anthem.log
def main(ctx):
    """ Loading demo data """
    import_suppliers(ctx)
    import_clients(ctx)
    import_products(ctx)
    import_locations(ctx)
    import_product_supplierinfo(ctx)
    import_pricelist_items(ctx)
    import_delivery_round_config(ctx)
