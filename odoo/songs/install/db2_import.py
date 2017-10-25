# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import os
from datetime import date

import anthem
from odoo import fields


PROD_IMPORTER_REFS = [
    'db2_import.db2_sale_importer',
    'db2_import.db2_purchase_importer',
]

INT_IMPORTER_REFS = [
    'db2_import.db2_importer_10_clients'
]


def add_years(d, years):
    """ Return a new date with added x years

    Take care of unexisting 29th February and replace it by 1st March

    """
    try:
        return d.replace(year=d.year + years)
    except Exception:
        # (just in case of unexisting 29th February take 1rst March)
        return d.replace(year=d.years + years, month=d.month + 1, day=1)


@anthem.log
def main(ctx):
    """ Setup and launch DB2 import tools

    Those tools will create the jobs to get data from DB2 in
    temporary tables

    We have a different behavior between integration and production database

    Production: all sales and purchases for 2 years
    Integration: sales for 10 clients for 2 years


    """

    env = os.environ.get("RUNNING_ENV")
    if env == 'production':
        years = 2
        importers = [ctx.env.ref(ref) for ref in PROD_IMPORTER_REFS]
    elif env == 'integration':
        years = 2
        importers = [ctx.env.ref(ref) for ref in INT_IMPORTER_REFS]
    else:
        # Don't automatically launch in dev/test env
        return

    today = date.today()
    end_date_str = fields.Date.to_string(today)
    __import__('pdb').set_trace()
    # x years ago
    start_date = add_years(today, -years)
    start_date_str = fields.Date.to_string(start_date)

    for rec in importers:
        rec.write({
            'mode': 'history',
            'date_start': start_date_str,
            'date_end': end_date_str,
        })
        rec.db2_import()
