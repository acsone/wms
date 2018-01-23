# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import os
from datetime import date
from dateutil.relativedelta import relativedelta

import anthem
from odoo import fields

"""
Songs to start the DB2 data importers to avoid the manual operation

Different importers will be launched depending on environment:

    PROD:
    + 2 years of sales
    + 2 years of purchases
    INT:
    + 3 months of sales
    + 3 months of purchases
    + 2 years of sales for 10 clients

"""

# importer refs with number of years, number of months
PROD_IMPORTER = [
    {'ref': 'db2_import.db2_sale_importer',
     'years': 2,
     'months': 0},
    {'ref': 'db2_import.db2_purchase_importer',
     'years': 2,
     'months': 0},
]

INT_IMPORTER = [
    {'ref': 'db2_import.db2_sale_importer',
     'years': 0,
     'months': 3},
    {'ref': 'db2_import.db2_purchase_importer',
     'years': 0,
     'months': 3},
    {'ref': 'db2_import.db2_importer_10_clients',
     'years': 2,
     'months': 0},
]


@anthem.log
def main(ctx):
    """ Setup and launch DB2 import tools

    Those tools will create the jobs to get data from DB2 in
    temporary tables

    We have a different behavior between integration and production database

    """

    env = os.environ.get("RUNNING_ENV")
    if env == 'production':
        importers = PROD_IMPORTER
    elif env == 'integration':
        importers = INT_IMPORTER
    else:
        # Don't automatically launch in dev/test env
        return

    today = date.today()
    end_date_str = fields.Date.to_string(today)

    for data in importers:
        rec = ctx.env.ref(data['ref'])
        start_date = today + relativedelta(years=-data['years'],
                                           months=-data['months'])
        start_date_str = fields.Date.to_string(start_date)
        rec.write({
            'mode': 'final_update',
            'date_start': start_date_str,
            'date_end': end_date_str,
        })
        rec.db2_import()
