# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem
from anthem.lyrics.records import create_or_update

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
        'implied_ids': [(4, ctx.env.ref('product.group_pricelist_item').id),(4, ctx.env.ref('product.group_sale_pricelist').id)]
    })    

@anthem.log
def import_price_categories(ctx):
    """ Importing prices categories from csv"""
    content = resource_stream(req, 'data/demo/product.price.category.csv')
    load_csv_stream(ctx, 'product.price.category', content, delimiter=',')

@anthem.log
def import_uom(ctx):
    """ Importing output locations from csv"""
    content = resource_stream(req, 'data/demo/product.uom.csv')
    load_csv_stream(ctx, 'stock.location', content, delimiter=',')

