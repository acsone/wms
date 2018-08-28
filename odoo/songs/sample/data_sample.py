# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from pkg_resources import resource_stream

import anthem
from anthem.lyrics.loaders import load_csv_stream, read_csv, load_rows
from anthem.lyrics.records import create_or_update
from ..common import req
from ..install.data_full import post_import_stock_bins


@anthem.log
def import_suppliers(ctx):
    """ Importing suppliers from csv """
    load_ctx = ctx.env.context.copy()
    load_ctx.update({'tracking_disable': True})

    # Deactivate VIES VAT Validation which is a second check on VAT
    ctx.env['res.company'].search([]).write({'vat_check_vies': False})

    Partner = ctx.env['res.partner'].with_context(load_ctx)

    with ctx.log(u"Importing suppliers"):
        content = resource_stream(req, 'data/sample/supplier.csv')
        load_csv_stream(ctx, Partner, content, delimiter=',')

    with ctx.log(u"Importing supplier contacts"):
        content = resource_stream(req, 'data/sample/supplier_contact.csv')
        load_csv_stream(ctx, Partner, content, delimiter=',')


@anthem.log
def import_clients(ctx):
    """ Importing clients from csv"""

    load_ctx = ctx.env.context.copy()
    load_ctx.update({'tracking_disable': True})
    Partner = ctx.env['res.partner'].with_context(load_ctx)

    # Deactivate VIES VAT Validation which is a second check on VAT
    ctx.env['res.company'].search([]).write({'vat_check_vies': False})

    with ctx.log(u"Importing customers"):
        content = resource_stream(req, 'data/sample/customer.csv')
        load_csv_stream(ctx, Partner, content, delimiter=',')

    with ctx.log(u"Importing customer relations to master customer"):
        content = resource_stream(req, 'data/sample/master_customer.csv')
        load_csv_stream(ctx, Partner, content, delimiter=',')

    with ctx.log(u"Importing customer addresses"):
        content = resource_stream(req, 'data/sample/customer_address.csv')
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
        content = resource_stream(req, 'data/sample/location.csv')
        load_csv_stream(ctx, Location, content, delimiter=',')
    with ctx.log(u"Importing reserve locations"):
        content = resource_stream(req, 'data/sample/locators_reserve.csv')
        load_csv_stream(ctx, Location, content, delimiter=',')
    with ctx.log(u"Importing parking locations"):
        content = resource_stream(req, 'data/sample/locators_parking.csv')
        load_csv_stream(ctx, Location, content, delimiter=',')
    with ctx.log(u"Importing output locations"):
        content = resource_stream(req, 'data/sample/chariots.csv')
        load_csv_stream(ctx, Location, content, delimiter=',')

    with ctx.log(u"Compute parent_left, parent_right"):
        ctx.env['stock.location']._parent_store_compute()


@anthem.log
def import_products(ctx):
    """ Importing products from csv"""
    values = {
        'name': "Divers",
        'default_code': "DIVERS",
        'list_price': 0.0
    }
    create_or_update(ctx, 'product.product',
                     '__setup__.product_other', values)
    load_ctx = ctx.env.context.copy()
    load_ctx.update({
        'tracking_disable': True,
        'no_connector_export': True,
        'force_archive_orderpoint': True,
        'disable_constrains_orderpoint': True})
    Product = ctx.env['product.product'].with_context(load_ctx)
    content = resource_stream(req, 'data/sample/product.csv')
    load_csv_stream(ctx, Product, content, delimiter=',')
    content = resource_stream(req, 'data/sample/additional_product.csv')
    load_csv_stream(ctx, Product, content, delimiter=',')
    content = resource_stream(req, 'data/sample/logistics_product.csv')
    load_csv_stream(ctx, Product, content, delimiter=';')
    # Importing data on product about 'Nouveauté' route
    content = resource_stream(req, 'data/sample/product_new_route_info.csv')
    load_csv_stream(ctx, Product, content, delimiter=',')
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
    content = resource_stream(req, 'data/sample/supplierinfo.csv')
    load_csv_stream(ctx, 'product.supplierinfo', content, delimiter=',')
    content = resource_stream(req, 'data/sample/supplierinfo_promo.csv')
    load_csv_stream(ctx, 'product.supplierinfo', content, delimiter=',')


@anthem.log
def import_pricelist_items(ctx):
    """ Importing pricelists from csv"""
    content = resource_stream(req, 'data/sample/pricelist_items.csv')
    load_csv_stream(ctx, 'product.pricelist.item', content, delimiter=',')


@anthem.log
def import_lots(ctx):
    """ Importing lots from csv"""
    load_ctx = ctx.env.context.copy()
    load_ctx.update({'tracking_disable': True})
    content = resource_stream(req, 'data/sample/stock_production_lot.csv')
    Lot = ctx.env['stock.production.lot'].with_context(load_ctx)
    load_csv_stream(ctx, Lot, content, delimiter=',')


@anthem.log
def import_inventory(ctx):
    """ Importing inventory from csv"""
    inventory = ctx.env['stock.inventory'].create({
        'name': 'Initial',
        })

    load_ctx = ctx.env.context.copy()
    load_ctx.update({'tracking_disable': True})
    ctx.env.context = load_ctx

    model = 'stock.inventory.line'
    content = resource_stream(req, 'data/sample/stock_inventory_line.csv')
    header, rows = read_csv(content)
    header.append('inventory_id/.id')
    new_rows = []
    for row in rows:
        row.append(inventory.id)
        new_rows.append(row)
    load_rows(ctx, model, header, list(new_rows))


@anthem.log
def import_inventory_without_lot(ctx):
    """ Importing inventory from csv"""
    inventory = ctx.env['stock.inventory'].create({
        'name': 'Initial (products without lot)',
        })

    load_ctx = ctx.env.context.copy()
    load_ctx.update({'tracking_disable': True})
    ctx.env.context = load_ctx

    model = 'stock.inventory.line'
    content = resource_stream(
        req, 'data/sample/stock_inventory_line_without_lot.csv')
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
    content = resource_stream(req, 'data/sample/product_stock_bin.csv')
    load_csv_stream(ctx, 'product.stock.bin', content, delimiter=',')


@anthem.log
def import_delivery_round_config(ctx):
    """ Importing delivery round config from csv"""
    content = \
        resource_stream(req, 'data/install/round.template.version.csv')
    load_csv_stream(ctx, 'round.template.version', content, delimiter=',')
    content = resource_stream(req, 'data/sample/delivery_template.csv')
    load_csv_stream(ctx, 'round.template', content, delimiter=',')
    content = resource_stream(req, 'data/sample/delivery_itinerary.csv')
    load_csv_stream(ctx, 'round.itinerary', content, delimiter=',')
    content = resource_stream(req, 'data/sample/delivery_clients.csv')
    load_csv_stream(ctx, 'round.itinerary.position', content, delimiter=',')


@anthem.log
def import_sale_orders(ctx):
    """ Importing sale orders from csv"""
    load_ctx = ctx.env.context.copy()
    load_ctx.update({'tracking_disable': True,
                     'no_connector_export': True})
    SaleOrder = ctx.env['sale.order'].with_context(load_ctx)
    content = resource_stream(req, 'data/sample/sale_order.csv')
    load_csv_stream(ctx, SaleOrder, content, delimiter=',')

    line_load_ctx = ctx.env.context.copy()
    line_load_ctx.update({
        'tracking_disable': True,
    })
    SaleOrderLine = ctx.env['sale.order.line'].with_context(line_load_ctx)
    content = resource_stream(req, 'data/sample/sale_order_line.csv')
    load_csv_stream(ctx, SaleOrderLine, content, delimiter=',')


@anthem.log
def main(ctx):
    """ Loading demo data """
    import_suppliers(ctx)
    import_clients(ctx)
    import_products(ctx)
    import_locations(ctx)
    import_sale_orders(ctx)
    import_product_supplierinfo(ctx)
    import_pricelist_items(ctx)
    import_lots(ctx)
    import_inventory(ctx)
    import_inventory_without_lot(ctx)
    import_stock_bins(ctx)
    import_delivery_round_config(ctx)
    post_import_stock_bins(ctx)
