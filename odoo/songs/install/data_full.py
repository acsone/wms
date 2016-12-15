# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from pkg_resources import resource_stream

import os
import anthem
from anthem.lyrics.loaders import load_csv_stream
from ..common import req


def get_file(req, default_file):
    """ Check if there is a DATA_FILE in environment else open default_file.

    DATA_FILE is passed by importer.sh when importing splitted file in parallel
    """
    try:
        file_path = os.environ['DATA_FILE']
    except KeyError:
        return resource_stream(req, default_file)
    else:
        return open(file_path)


@anthem.log
def import_suppliers(ctx):
    """ Importing suppliers from csv """

    content = get_file(req, 'data/install/supplier.csv')
    load_csv_stream(ctx, 'res.partner', content, delimiter=',')


@anthem.log
def import_clients(ctx):
    """ Importing clients from csv"""
    content = get_file(req, 'data/install/customer.csv')
    load_csv_stream(ctx, 'res.partner', content, delimiter=',')


@anthem.log
def import_products(ctx):
    """ Importing products from csv"""
    content = get_file(req, 'data/install/product.csv')
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
    content = get_file(req, 'data/install/product.csv')
    load_csv_stream(ctx, 'product.supplierinfo', content, delimiter=',')


@anthem.log
def import_pricelist_items(ctx):
    """ Importing pricelists from csv"""
    content = get_file(req, 'data/install/pricelist_items.csv')
    load_csv_stream(ctx, 'product.pricelist.item', content, delimiter=',')


@anthem.log
def import_locators(ctx):
    """ Importing locators from csv"""
    content = resource_stream(req, 'data/demo/locators_subset.csv')
    load_csv_stream(ctx, 'stock.location', content, delimiter=',')
    content = resource_stream(req, 'data/demo/locators_reserve.csv')
    load_csv_stream(ctx, 'stock.location', content, delimiter=',')
    content = resource_stream(req, 'data/demo/locators_parking.csv')
    load_csv_stream(ctx, 'stock.location', content, delimiter=',')


@anthem.log
def import_output_locations(ctx):
    """ Importing output locations from csv"""
    content = resource_stream(req, 'data/demo/chariots.csv')
    load_csv_stream(ctx, 'stock.location', content, delimiter=',')


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
    """ Loading full data (But in this function only small files,
    other files will be import by importer.sh)
    """
    # Putting some demo data in full mode because we don't have yet real data
    import_locators(ctx)
    import_output_locations(ctx)
    import_delivery_round_config(ctx)
