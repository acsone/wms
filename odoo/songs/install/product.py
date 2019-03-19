# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem
from anthem.lyrics.loaders import load_csv_stream
from anthem.lyrics.records import create_or_update
from pkg_resources import resource_stream

from ..common import req


@anthem.log
def set_customer_lead_time(ctx):
    create_or_update(
        ctx,
        'ir.values',
        '__setup__.product_customer_lead',
        {
            'key': 'default',
            'name': 'sale_delay',
            'model': 'product.template',
            'value_unpickle': '0',
        },
    )


@anthem.log
def import_accounting_products(ctx):
    """ Importing accounting products """
    content = resource_stream(req, 'data/install/accounting_products.csv')
    load_csv_stream(ctx, 'product.product', content, delimiter=',')


@anthem.log
def zero_digits_for_uom(ctx):
    """Set digits of Decimal Accuracy for product uom to 0.
    """
    ctx.env.ref('product.decimal_product_uom').write({'digits': 0})


@anthem.log
def setup_product_default_code_sequence(ctx):
    """ Initialize sequence for default_code on product

    The highest numeric id in db2 is 9999999.
    But the last created ids at the time of writting this are
    5840422, 5840504, 5062001, 8286585, 5311165, 5151528
    """
    sequence_start = 10000000
    ref_seq = ctx.env.ref('product_sequence.seq_product_auto')
    ref_seq.prefix = ''
    seq_name = 'ir_sequence_%03d' % ref_seq.id
    sql = 'ALTER SEQUENCE %s RESTART WITH %d;' % (seq_name, sequence_start)
    ctx.env.cr.execute(sql)


@anthem.log
def disable_quickcreate(ctx):
    """ Prevent quick create of product """
    ctx.env.ref('product.model_product_product').avoid_quick_create = True


@anthem.log
def set_not_print_flag_on_materiel_product(ctx):
    """Set the flag do not print label on materiel products"""
    categ_materiel = ctx.env.ref('specific_data.product_categ_materiel')

    products = ctx.env['product.template'].search(
        [('categ_id', 'child_of', categ_materiel.id)]
    )
    products.write({'is_do_not_print_label': True})


@anthem.log
def main(ctx):
    """ Configuring products """
    set_customer_lead_time(ctx)
    import_accounting_products(ctx)
    zero_digits_for_uom(ctx)
    disable_quickcreate(ctx)
    set_not_print_flag_on_materiel_product(ctx)
