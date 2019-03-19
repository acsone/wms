# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import os
from datetime import date
from distutils.util import strtobool

import anthem
from dateutil.relativedelta import relativedelta

from odoo import fields

"""
Songs to start the DB2 data importers to avoid the manual operation

By default different importers will be launched depending on environment:

    PROD:
    + 2 years of sales
    + 2 years of purchases
    INT:
    + 3 months of sales
    + 3 months of purchases
    + 2 years of sales for 10 clients

"""

# importer refs with number of years, number of months
BASE_IMPORTER = [
    {
        'ref': 'db2_import.db2_sale_importer',
        'csv_until': '2018-04-01',
    },  # csv_until is excluded date
    {'ref': 'db2_import.db2_purchase_importer', 'csv_until': '2018-04-01'},
]

# importer for selection of 10 clients
EXT_IMPORTER = [
    {
        'ref': 'db2_import.db2_importer_10_clients',
        'is_ext': True,
        'csv_until': '2018-04-01',
    }
]


@anthem.log
def main(ctx):
    """ Setup and launch DB2 import tools

    Those tools will create the jobs to get data from DB2 in
    temporary tables

    We have a different behavior between integration and production database

    """

    importers = BASE_IMPORTER

    env = os.environ.get("RUNNING_ENV")
    mode = os.environ.get("DB2IMPORT_MODE")
    years = os.environ.get("DB2IMPORT_YEARS")
    months = os.environ.get("DB2IMPORT_MONTHS")
    use_ext = os.environ.get("DB2IMPORT_10CLI")
    ext_years = os.environ.get("DB2IMPORT_10CLI_YEARS")
    ext_months = os.environ.get("DB2IMPORT_10CLI_MONTHS")

    if years:
        years = int(years)
    else:
        years = 0
    if months:
        months = int(months)
    else:
        months = 0
    if ext_years:
        ext_years = int(ext_years)
    else:
        ext_years = 0
    if ext_months:
        ext_months = int(ext_months)
    else:
        ext_months = 0

    # redefine default values depending on environment
    if env == 'prod':
        if not mode:
            mode = 'history'
        if not years and not months:
            # default to full scale import
            years = 2
            months = 0
        # Never use ext in PROD
        use_ext = False
    elif env == 'integration':
        if not mode:
            mode = 'final_update'
        if not years and not months:
            # default to reduced import
            years = 0
            months = 3
        if use_ext is None:
            use_ext = True
        else:
            use_ext = strtobool(use_ext)
        if not ext_years and not ext_months:
            ext_years = 2
            ext_months = 0

    else:
        # Don't automatically launch in dev/test env
        return

    if use_ext:
        if ext_years > years or ext_years == years and ext_months > months:
            importers.extend(EXT_IMPORTER)
        else:
            # no need for extension if it extends nothing
            use_ext = False

    today = date.today()
    end_date_str = fields.Date.to_string(today)
    start_date = today + relativedelta(years=-years, months=-months)
    start_date_str = fields.Date.to_string(start_date)

    for data in importers:
        rec = ctx.env.ref(data['ref'])
        # reduce the range to what is already imported in main
        if use_ext and data.get('is_ext'):
            end_date = start_date + relativedelta(days=-1)
            end_date_str = fields.Date.to_string(end_date)
            start_date = today + relativedelta(
                years=-ext_years, months=-ext_months
            )
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
