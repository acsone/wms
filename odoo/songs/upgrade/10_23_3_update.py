# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from pkg_resources import resource_stream

import anthem
from anthem.lyrics.loaders import load_csv_stream

from ..common import req


@anthem.log
def remove_pickingtype_humain(ctx):
    picking_type = ctx.env.ref(
        '__setup__.stock_picking_type_humain',
        raise_if_not_found=False
    )
    if picking_type:
        picking_type.unlink()
    location = ctx.env.ref(
        '__setup__.stock_location_pharma',
        raise_if_not_found=False
    )
    if location:
        location.unlink()


@anthem.log
def add_missing_antibiotic_taxes(ctx):
    """ Add missing antibiotic taxes from account tax template """
    company = ctx.env.ref('base.main_company')

    missing_taxes_xmlid = (
        'l10n_be_antibiotic_tax.antibiotic_012_out',
        'l10n_be_antibiotic_tax.antibiotic_024_out',
        'l10n_be_antibiotic_tax.antibiotic_033_out',
        'l10n_be_antibiotic_tax.antibiotic_065_out',
        'l10n_be_antibiotic_tax.antibiotic_214_out',
        'l10n_be_antibiotic_tax.antibiotic_012_in',
        'l10n_be_antibiotic_tax.antibiotic_024_in',
        'l10n_be_antibiotic_tax.antibiotic_033_in',
        'l10n_be_antibiotic_tax.antibiotic_066_in',
        'l10n_be_antibiotic_tax.antibiotic_244_in'
    )
    for missing_tax_xmlid in missing_taxes_xmlid:
        template = ctx.env.ref(missing_tax_xmlid)
        # The method generate_tax will create the tax
        # OR update if the tax already existing
        template._generate_tax(company)

# FULL MODE Section


@anthem.log
def import_products(ctx):
    """ Clean indicated price in products by loading a csv"""
    load_ctx = ctx.env.context.copy()
    load_ctx.update({'tracking_disable': True})
    Product = ctx.env['product.product'].with_context(load_ctx)
    content = resource_stream(
        req, 'data/upgrade/10.23.3/product-clean-indicated-price.csv')
    load_csv_stream(ctx, Product, content, delimiter=',')


@anthem.log
def post(ctx):
    """ POST 10.23.3 """
    remove_pickingtype_humain(ctx)
    add_missing_antibiotic_taxes(ctx)


@anthem.log
def post_full(ctx):
    """ POST FULL 10.23.3 """
    import_products(ctx)
