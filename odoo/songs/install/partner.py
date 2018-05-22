# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from pkg_resources import resource_stream

import anthem
from anthem.lyrics.loaders import load_csv_stream

from ..common import req


@anthem.log
def create_customer_category(ctx):
    """ Importing customer categories from csv """
    content = resource_stream(req, 'data/install/customer.category.csv')
    load_csv_stream(ctx, 'res.partner.category', content, delimiter=',')


@anthem.log
def create_supplier_category(ctx):
    """ Importing supplier categories from csv """
    content = resource_stream(req, 'data/install/supplier.category.csv')
    load_csv_stream(ctx, 'res.partner.category', content, delimiter=',')


@anthem.log
def setup_customer_ref(ctx):
    """ Setup partner ref sequence

    Start with 100'000 because the highest value for supplier ref is
    around 95'000 in the imported data
    """
    sequence_start = 100000
    ref_seq = ctx.env.ref('base_partner_sequence.seq_res_partner')
    ref_seq.prefix = ''
    # Change the starting sequence in postgres
    seq_name = 'ir_sequence_%03d' % ref_seq.id
    sql = ('ALTER SEQUENCE %s RESTART WITH %d;' % (seq_name, sequence_start))
    ctx.env.cr.execute(sql)


@anthem.log
def create_legal_entity(ctx):
    """ Importing legal entities from csv """
    content = resource_stream(req, 'data/install/legal.entity.csv')
    load_csv_stream(ctx, 'legal.entity', content, delimiter=',')


@anthem.log
def main(ctx):
    """ Configuring partner """
    create_customer_category(ctx)
    create_supplier_category(ctx)
