# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from pkg_resources import resource_stream

import anthem
from anthem.lyrics.loaders import load_csv_stream
from ..common import req


@anthem.log
def sale_setup(ctx):
    """ Settings for the Sale module """
    employee_group = ctx.env.ref('base.group_user')

    # Active multi Unit of measure
    employee_group.write({
        'implied_ids': [(4, ctx.env.ref('product.group_uom').id)]
    })

    # Active sales prices based formula
    employee_group.write({
        'implied_ids': [
         (4, ctx.env.ref('product.group_pricelist_item').id),
         (4, ctx.env.ref('product.group_sale_pricelist').id)]
    })


@anthem.log
def import_price_categories(ctx):
    """ Importing prices categories from csv"""
    content = resource_stream(req, 'data/install/product.price.category.csv')
    load_csv_stream(ctx, 'product.price.category', content, delimiter=',')


@anthem.log
def import_uom(ctx):
    """ Importing unit of measure """
    content = resource_stream(req, 'data/install/product.uom.csv')
    load_csv_stream(ctx, 'product.uom', content, delimiter=',')


@anthem.log
def import_crm_team(ctx):
    """ Importing sales teams """
    content = resource_stream(req, 'data/install/crm.team.csv')
    load_csv_stream(ctx, 'crm.team', content, delimiter=',')


@anthem.log
def import_pricelist(ctx):
    """ Importing sales teams """
    content = resource_stream(req, 'data/install/product.pricelist.csv')
    load_csv_stream(ctx, 'product.pricelist', content, delimiter=',')


@anthem.log
def main(ctx):
    """ run scenario """
    sale_setup(ctx)
    import_price_categories(ctx)
    import_uom(ctx)
    import_crm_team(ctx)
    import_pricelist(ctx)
