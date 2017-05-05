# -*- coding: utf-8 -*-
# Author: Julien Coux
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from pkg_resources import resource_stream

import anthem
from anthem.lyrics.records import create_or_update
from anthem.lyrics.loaders import load_csv_stream

from ...common import req


@anthem.log
def create_picking_types(ctx):

    types = [
        {'xmlid': 'stock.picking_type_in',
         'use_create_lots': False,
         'use_existing_lots': True,
         },
    ]
    for record in types:
        xmlid = record.pop('xmlid')
        create_or_update(ctx, 'stock.picking.type', xmlid, record)


@anthem.log
def import_account_journal(ctx):

    # Import account journal
    content = resource_stream(req, 'data/install/account.journal.csv')
    load_csv_stream(ctx, 'account.journal', content, delimiter=',')

    # Set the flag "update_posted" on following journals
    # These journals have no XMLid
    journals_to_flag = ctx.env['account.journal'].search([
        ('code', 'in', ['STJ', 'BILL', 'EXP', 'INV', 'MISC'])
    ])
    journals_to_flag.write({
        'update_posted': True
    })


@anthem.log
def main(ctx):
    """ Update 10.1.0 """
    create_picking_types(ctx)
    import_account_journal(ctx)
