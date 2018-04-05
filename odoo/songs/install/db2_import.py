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
     'months': 0,
     'csv_until': '2018-04-01'},
    {'ref': 'db2_import.db2_purchase_importer',
     'years': 2,
     'months': 0,
     'csv_until': '2018-04-01'},
]

INT_IMPORTER = [
    {'ref': 'db2_import.db2_sale_importer',
     'years': 0,
     'months': 3,
     'csv_until': '2018-04-01'},
    {'ref': 'db2_import.db2_purchase_importer',
     'years': 0,
     'months': 3,
     'csv_until': '2018-04-01'},
    {'ref': 'db2_import.db2_importer_10_clients',
     'years': 2,
     'months': 0,
     'csv_until': '2018-04-01'},
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
        mode = 'history'
    elif env == 'integration':
        importers = INT_IMPORTER
        # To uncomment when we want to do a full scale test of the import
        # but only on the c2c_platform
        # last time done on:
        # - 10.18.0
        # if os.environ.get('C2C_PLATFORM') == 'True':
        #     importers = PROD_IMPORTER
        mode = 'final_update'
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
        csv_until = data.get('csv_until')
        values = {
            'mode': mode,
            'date_start': start_date_str,
            'date_end': end_date_str,
        }
        rec.write(values)
        if csv_until:
            for table in rec.table_ids:
                table.csv_until = csv_until
        rec.db2_import()
