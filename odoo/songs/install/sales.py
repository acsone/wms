# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from pkg_resources import resource_stream

import anthem
from anthem.lyrics.loaders import load_csv_stream
from ..common import define_settings
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

    # Default invoice
    define_settings(ctx,
                    'sale.config.settings',
                    {'default_invoice_policy': 'delivery'})


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
    """ Importing pricelist """
    content = resource_stream(req, 'data/install/product.pricelist.csv')
    load_csv_stream(ctx, 'product.pricelist', content, delimiter=',')


@anthem.log
def clean_pricelist_item(ctx):
    """ Deleting pricelist items """
    ctx.env.cr.execute("""
        DELETE FROM product_pricelist_item
        WHERE id NOT IN (
            SELECT res_id
            FROM ir_model_data
            WHERE model='product.pricelist.item'
        )
    """)


@anthem.log
def import_pricelist_item(ctx):
    """ Importing product pricelist """
    content = resource_stream(req, 'data/install/product.pricelist.item.csv')
    load_csv_stream(ctx, 'product.pricelist.item', content, delimiter=',')


@anthem.log
def load_res_title(ctx):
    """ Import Titles  """
    csv_content = resource_stream(req, 'data/install/res.partner.title.csv')
    load_csv_stream(ctx, 'res.partner.title', csv_content, delimiter=',')


@anthem.log
def clean_title(ctx):

    for xmlid in ('base.res_partner_title_sir', 'base.res_partner_title_miss'):
        title = ctx.env.ref(xmlid, raise_if_not_found=False)
        if title:
            title.unlink()


@anthem.log
def main(ctx):
    """ run scenario """
    sale_setup(ctx)
    import_price_categories(ctx)
    import_uom(ctx)
    import_crm_team(ctx)
    import_pricelist(ctx)
    clean_pricelist_item(ctx)
    import_pricelist_item(ctx)
    load_res_title(ctx)
    clean_title(ctx)
