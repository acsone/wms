# -*- coding: utf-8 -*-
# Copyright 2016-2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem
from anthem.lyrics.loaders import load_csv_stream
from pkg_resources import resource_stream

from mappings import COUNTRY, PRODUCT_PURCHASE_VAT, PRODUCT_SALE_VAT

from ..common import create_default_value, req


@anthem.log
def import_delivery_carriers(ctx):
    """ Importing carriers from csv """
    load_ctx = ctx.env.context.copy()
    load_ctx.update({'tracking_disable': True})
    Carrier = ctx.env['delivery.carrier'].with_context(load_ctx)
    content = resource_stream(req, 'data/install/delivery.carrier.csv')
    load_csv_stream(ctx, Carrier, content, delimiter=',')
    # load NL translations (DE translations do not exists)
    with ctx.log(u"Load NL translations"):
        Carrier = Carrier.with_context(lang='nl_BE')
        content = resource_stream(req, 'data/install/delivery.carrier-nl.csv')
        load_csv_stream(ctx, Carrier, content, delimiter=',')


@anthem.log
def set_default_carrier_id_on_sale_order(ctx):
    """Set a default value for the carrier id on sale order."""
    ctx.env['ir.values'].set_default(
        'sale.order',
        'carrier_id',
        ctx.env.ref('__setup__.deliver_carrier_alcyon').id,
    )


@anthem.log
def default_values(ctx):
    """ Setting default values """
    for company in ctx.env['res.company'].search([]):
        create_default_value(
            ctx, 'product.template', 'type', 'product', company.id
        )


@anthem.log
def define_esb_ref_on_countries(ctx):
    """ Define esb_res on countries """
    for esb_ref, xmlid in COUNTRY.iteritems():
        country = ctx.env.ref(xmlid)
        country.esb_ref = esb_ref


@anthem.log
def define_esb_ref_on_carrier_shipping(ctx):
    ctx.env.ref('specific_data.deliver_carrier_alcyon_product_product').write(
        {'esb_ref': '1'}
    )


@anthem.log
def define_esb_ref_on_taxes(ctx):
    """ Define esb_res on taxes """
    for taxes in [PRODUCT_SALE_VAT, PRODUCT_PURCHASE_VAT]:
        for esb_ref, xmlid in taxes.iteritems():
            tax = ctx.env.ref(xmlid)
            tax.esb_ref = esb_ref


@anthem.log
def import_payment_modes(ctx):
    """ Importing payment modes from csv"""
    content = resource_stream(req, 'data/install/account.payment.method.csv')
    load_csv_stream(ctx, 'account.payment.method', content, delimiter=',')
    content = resource_stream(req, 'data/install/account.payment.mode.csv')
    load_csv_stream(ctx, 'account.payment.mode', content, delimiter=',')


@anthem.log
def rename_payment_method(ctx):
    """ Rename Manual by Domiciliation """
    payment_method = ctx.env.ref(
        'account.account_payment_method_manual_out', raise_if_not_found=False
    )
    if payment_method:
        payment_method.write({'name': 'Domiciliation'})


@anthem.log
def main(ctx):
    """ Loading data """
    default_values(ctx)
    import_delivery_carriers(ctx)
    set_default_carrier_id_on_sale_order(ctx)
    define_esb_ref_on_countries(ctx)
    define_esb_ref_on_taxes(ctx)
    define_esb_ref_on_carrier_shipping(ctx)
    import_payment_modes(ctx)
    rename_payment_method(ctx)
