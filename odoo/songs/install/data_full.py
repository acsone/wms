# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from pkg_resources import resource_stream

import os
import anthem
from anthem.lyrics.loaders import load_csv_stream, read_csv, load_rows
from anthem.lyrics.records import create_or_update
from ..common import req


def get_files(req, default_file):
    """ Check if there is a DATA_DIR in environment else open default_file.

    DATA_DIR is passed by importer.sh when importing splitted file in parallel

    Returns a generator of file to import as DATA_DIR can contain a split of
    csv file
    """
    try:
        dir_path = os.environ['DATA_DIR']
    except KeyError:
        yield resource_stream(req, default_file)
    else:
        file_list = os.listdir(dir_path)
        for file_name in file_list:
            file_path = os.path.join(dir_path, file_name)
            yield open(file_path)


@anthem.log
def import_suppliers(ctx):
    """ Importing suppliers from csv """

    load_ctx = ctx.env.context.copy()
    load_ctx.update({'tracking_disable': True})
    Partner = ctx.env['res.partner'].with_context(load_ctx)
    for content in get_files(req, 'data/install/supplier.csv'):
        load_csv_stream(ctx, Partner, content, delimiter=',')


def import_additional_suppliers_data(ctx):
    """ Importing additional supplier data from csv """

    load_ctx = ctx.env.context.copy()
    load_ctx.update({'tracking_disable': True})
    Partner = ctx.env['res.partner'].with_context(load_ctx)
    for content in get_files(req, 'data/install/supplier_add_data.csv.csv'):
        load_csv_stream(ctx, Partner, content, delimiter=',')


@anthem.log
def import_clients(ctx):
    """ Importing clients from csv"""

    load_ctx = ctx.env.context.copy()
    load_ctx.update({'tracking_disable': True})
    Partner = ctx.env['res.partner'].with_context(load_ctx)
    for content in get_files(req, 'data/install/customer.csv'):
        load_csv_stream(ctx, Partner, content, delimiter=',')


@anthem.log
def import_clients_addresses(ctx):
    """ Importing clients addresses from csv"""

    load_ctx = ctx.env.context.copy()
    load_ctx.update({'tracking_disable': True})
    Partner = ctx.env['res.partner'].with_context(load_ctx)
    for content in get_files(req, 'data/install/customer_address.csv'):
        load_csv_stream(ctx, Partner, content, delimiter=',')


@anthem.log
def create_product_other(ctx):
    """ Create product 'Other' used when importing sale orders """
    values = {
        'name': "Divers",
        'default_code': "DIVERS",
        'list_price': 0.0
    }
    create_or_update(ctx, 'product.product',
                     '__setup__.product_other', values)


@anthem.log
def import_products(ctx):
    """ Importing products from csv"""
    load_ctx = ctx.env.context.copy()
    load_ctx.update({'tracking_disable': True})
    Product = ctx.env['product.product'].with_context(load_ctx)
    file_csv = 'data/install/product.csv'
    for content in get_files(req, file_csv):
        load_csv_stream(ctx, Product, content, delimiter=',')


@anthem.log
def post_import_products(ctx):
    # Computed fields on product.template are not set for archived product
    # copy the values from product.product
    ctx.env.cr.execute("""
        UPDATE product_template as tmpl
        SET active=prod.active, default_code=prod.default_code
        FROM product_product as prod
        WHERE tmpl.id = prod.id AND prod.active=False
    """)


@anthem.log
def import_product_supplierinfo(ctx):
    """ Importing product supplier infos from csv"""
    for content in get_files(req, 'data/install/supplierinfo.csv'):
        load_csv_stream(ctx, 'product.supplierinfo', content, delimiter=',')


@anthem.log
def import_pricelist_items(ctx):
    """ Importing pricelists from csv"""
    for content in get_files(req, 'data/install/pricelist_items.csv'):
        load_csv_stream(ctx, 'product.pricelist.item', content, delimiter=',')


@anthem.log
def import_wh_family_locations(ctx):
    """ Importing family locations from csv"""

    load_ctx = ctx.env.context.copy()
    load_ctx.update({'defer_parent_store_computation': 'manually'})
    Location = ctx.env['stock.location'].with_context(load_ctx)
    content = resource_stream(req, 'data/install/location_family.csv')
    load_csv_stream(ctx, Location, content, delimiter=',')


@anthem.log
def import_wh_locations(ctx):
    """ Importing warehouse locations from csv"""

    load_ctx = ctx.env.context.copy()
    load_ctx.update({'defer_parent_store_computation': 'manually'})
    Location = ctx.env['stock.location'].with_context(load_ctx)
    for content in get_files(req, 'data/install/location.csv'):
        load_csv_stream(ctx, Location, content, delimiter=',')


@anthem.log
def import_other_locations(ctx):
    """ Importing other locations from csv"""

    load_ctx = ctx.env.context.copy()
    load_ctx.update({'defer_parent_store_computation': 'manually'})
    Location = ctx.env['stock.location'].with_context(load_ctx)
    with ctx.log(u"Importing reserve locations"):
        content = resource_stream(req, 'data/sample/locators_reserve.csv')
        load_csv_stream(ctx, Location, content, delimiter=',')
    with ctx.log(u"Importing parking locations"):
        content = resource_stream(req, 'data/sample/locators_parking.csv')
        load_csv_stream(ctx, Location, content, delimiter=',')


@anthem.log
def location_compute_parents(ctx):
    """Compute parent_left, parent_right"""
    ctx.env['stock.location']._parent_store_compute()


@anthem.log
def import_delivery_round_config(ctx):
    """ Importing delivery round config from csv"""
    content = \
        resource_stream(req, 'data/install/round.template.version.csv')
    load_csv_stream(ctx, 'round.template.version', content, delimiter=',')

    content = resource_stream(req, 'data/install/delivery_template.csv')
    load_csv_stream(ctx, 'round.template', content, delimiter=',')
    content = resource_stream(
        req, 'data/install/delivery.carrier.template.csv')
    load_csv_stream(ctx, 'round.template', content, delimiter=',')

    content = resource_stream(req, 'data/install/delivery_itinerary.csv')
    load_csv_stream(ctx, 'round.itinerary', content, delimiter=',')
    content = resource_stream(req, 'data/install/delivery_clients.csv')
    load_csv_stream(ctx, 'round.itinerary.position', content, delimiter=',')


@anthem.log
def import_delivery_carriers_round(ctx):
    """ Importing carriers - delivery round mapping from csv """
    load_ctx = ctx.env.context.copy()
    load_ctx.update({'tracking_disable': True})
    Carrier = ctx.env['delivery.carrier'].with_context(load_ctx)
    content = resource_stream(req, 'data/install/delivery.carrier.round.csv')
    load_csv_stream(ctx, Carrier, content, delimiter=',')


@anthem.log
def import_lots(ctx):
    """ Importing lots from csv"""
    load_ctx = ctx.env.context.copy()
    load_ctx.update({'tracking_disable': True})
    Lot = ctx.env['stock.production.lot'].with_context(load_ctx)
    for content in get_files(req, 'data/install/stock_production_lot.csv'):
        load_csv_stream(ctx, Lot, content, delimiter=',')


@anthem.log
def import_inventory(ctx):
    """ Importing inventory from csv"""
    values = {
        'name': 'Initial',
        }
    inventory = create_or_update(ctx, 'stock.inventory',
                                 '__setup__.initial_inventory', values)

    load_ctx = ctx.env.context.copy()
    load_ctx.update({'tracking_disable': True})
    ctx.env.context = load_ctx

    model = 'stock.inventory.line'
    content = resource_stream(req, 'data/install/stock_inventory_line.csv')
    header, rows = read_csv(content)
    header.append('inventory_id/.id')
    new_rows = []
    for row in rows:
        row.append(inventory.id)
        new_rows.append(row)
    load_rows(ctx, model, header, list(new_rows))


@anthem.log
def import_inventory_without_lot(ctx):
    """ Importing second inventory without lots from csv"""
    values = {
        'name': 'Initial (products without lot)',
    }
    inventory = create_or_update(ctx, 'stock.inventory',
                                 '__setup__.initial_inventory_no_lot', values)

    load_ctx = ctx.env.context.copy()
    load_ctx.update({'tracking_disable': True})
    ctx.env.context = load_ctx

    model = 'stock.inventory.line'
    content = resource_stream(
        req, 'data/install/stock_inventory_line_without_lot.csv')
    header, rows = read_csv(content)
    header.append('inventory_id/.id')
    new_rows = []
    for row in rows:
        row.append(inventory.id)
        new_rows.append(row)
    load_rows(ctx, model, header, list(new_rows))


@anthem.log
def import_stock_bins(ctx):
    """ Importing Stock Bins"""
    for content in get_files(req, 'data/install/product_stock_bin.csv'):
        load_csv_stream(ctx, 'product.stock.bin', content, delimiter=',')


@anthem.log
def post_import_stock_bins(ctx):
    """ Add route on product stocked depending on locators.

    This is a post correction of the csv file product_stock_bin.csv
    for both demo and full data modes.

    Plus add "Nouveauté" route if the former locator has only one letter
    and has route purchase.route_warehouse0_buy.
    As locator with 1 letter is not imported we take and clean this information
    from description_picking field on the product.

    """
    StockBin = ctx.env['product.stock.bin']

    food_route = ctx.env.ref('__setup__.stock_location_route_pick_ali')
    fridge_route = ctx.env.ref('__setup__.stock_location_route_pick_froid')
    mat_route = ctx.env.ref('__setup__.stock_location_route_pick_materiel')
    med_route = ctx.env.ref('__setup__.stock_location_route_pick_medoc')
    new_route = ctx.env.ref('__setup__.stock_location_route_new')

    family_map = [
        ('A', food_route),
        ('Q', fridge_route),
        ('E', mat_route),
        ('P', mat_route),
        ('G', med_route),
    ]

    cr = ctx.env.cr

    for family_letter, route in family_map:
        family = ctx.env.ref('__import__.location_family_%s' % family_letter)
        domain = [('bin_location_id', 'child_of', family.id)]
        product_bins = StockBin.search(domain)
        if not product_bins:
            continue
        products = product_bins.mapped('product_id')

        cr.execute(
            "INSERT INTO stock_route_product (product_id, route_id)"
            "  SELECT id, %s FROM product_template"
            "  WHERE id in %s"
            "    AND id NOT IN ("
            "      SELECT product_id FROM stock_route_product"
            "      WHERE route_id = %s)",
            (route.id, tuple(products.ids), route.id))

    def sql_create_routes(letter, route):
        cr.execute(
            "INSERT INTO stock_route_product (product_id, route_id)"
            "  SELECT id, %s FROM product_template"
            "  WHERE description_picking = %s"
            "    AND id NOT IN ("
            "      SELECT product_id FROM stock_route_product"
            "      WHERE route_id = %s)",
            (route.id, family_letter, route.id))

    for family_letter, route in family_map:
        sql_create_routes(family_letter, route)
        sql_create_routes(family_letter, new_route)


@anthem.log
def main(ctx):
    """ Loading full data (But in this function only small files,
    other files will be import by importer.sh)
    """
    create_product_other(ctx)
    # Putting some demo data in full mode because we don't have yet real data
    import_delivery_round_config(ctx)
    import_delivery_carriers_round(ctx)
