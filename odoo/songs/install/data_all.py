# -*- coding: utf-8 -*-
# Copyright 2016-2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from pkg_resources import resource_stream

import anthem
from anthem.lyrics.loaders import load_csv_stream
from ..common import req, create_default_value
from mappings import COUNTRY, PRODUCT_SALE_VAT, PRODUCT_PURCHASE_VAT


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
def default_values(ctx):
    """ Setting default values """
    for company in ctx.env['res.company'].search([]):
        create_default_value(ctx,
                             'product.template',
                             'type',
                             'product',
                             company.id)


@anthem.log
def define_esb_ref_on_countries(ctx):
    """ Define esb_res on countries """
    for esb_ref, xmlid in COUNTRY.iteritems():
        country = ctx.env.ref(xmlid)
        country.esb_ref = esb_ref


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
    content = resource_stream(req, 'data/install/account.payment.mode.csv')
    load_csv_stream(ctx, 'account.payment.mode', content, delimiter=',')


@anthem.log
def main(ctx):
    """ Loading data """
    default_values(ctx)
    import_delivery_carriers(ctx)
    define_esb_ref_on_countries(ctx)
    define_esb_ref_on_taxes(ctx)
    import_payment_modes(ctx)
