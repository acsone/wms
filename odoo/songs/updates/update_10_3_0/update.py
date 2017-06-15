# -*- coding: utf-8 -*-
# Copyright 2017 Okia SPRL, Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from pkg_resources import resource_stream

import anthem
from anthem.lyrics.loaders import load_csv_stream

from ...common import req


@anthem.log
def change_communication_type(ctx):
    """
    Change the type of communication of all customers and suppliers
    to have a structured communication (random)
    :param ctx:
    :return:
    """
    partners = ctx.env['res.partner'].search(['|',
                                              ('customer', '=', True),
                                              ('supplier', '=', True)])
    partners.write({
        'out_inv_comm_type': 'bba',
        'out_inv_comm_algorithm': 'random',
    })


@anthem.log
def adapt_chart_of_account(ctx):
    """ Adapt chart of account """
    content = resource_stream(
        req,
        'data/updates/update_10_3_0/01_add_account.account.csv'
    )
    load_csv_stream(ctx, 'account.account', content, delimiter=',')

    content = resource_stream(
        req,
        'data/updates/update_10_3_0/'
        '02_all_without_reconcile_account.account.csv'
    )
    load_csv_stream(ctx, 'account.account', content, delimiter=',')


@anthem.log
def main(ctx):
    """ Update 10.3.0 """
    change_communication_type(ctx)
    adapt_chart_of_account(ctx)
