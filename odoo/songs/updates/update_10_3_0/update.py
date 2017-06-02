# -*- coding: utf-8 -*-
# Copyright 2017 Okia SPRL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from pkg_resources import resource_stream

import anthem
from anthem.lyrics.records import create_or_update
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
def main(ctx):
    """ Update 10.3.0 """
    change_communication_type(ctx)
