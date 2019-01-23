# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

"""
This is an Anthem song to be executed manually when ready to activate
the cron jobs for the ESB exports.

To use set the day_first_export variable accordingly and then run
the main script. The time set for each cron job are in UTC.

The last_export for the stock must be set as well. The idea is
to set it to a datetime a little posterior to the end of the data migration
procees. Because there should not be the need to export all stock info to
Magento as they should have been kept up to date by the AS400 until then.

"""

import anthem

module = 'connector_esb'

# Set those two variables accordingly before running the script
day_first_export = '2018-10-01'
stock_last_export = '2018-10-01 00:00:01'

all_cron = [
        {
            'xmlid': 'ir_cron_esb_export_product',
            'nextcall': day_first_export + ' ' + '00:00:00'
        },
        {
            'xmlid': 'ir_cron_esb_export_pharmacy',
            'nextcall': day_first_export + ' ' + '00:30:00'
        },
        {
            'xmlid': 'ir_cron_esb_export_customer_morning',
            'nextcall': day_first_export + ' ' + '01:00:00'
        },
        {
            'xmlid': 'ir_cron_esb_export_customer_afternoon',
            'nextcall': day_first_export + ' ' + '15:30:00'
        },
        {
            'xmlid': 'ir_cron_esb_export_customer_address_morning',
            'nextcall': day_first_export + ' ' + '01:15:00'
        },
        {
            'xmlid': 'ir_cron_esb_export_customer_address_afternoon',
            'nextcall': day_first_export + ' ' + '15:45:00'
        },
        {
            'xmlid': 'ir_cron_esb_export_promotion_alcyon',
            'nextcall': day_first_export + ' ' + '02:00:00'
        },
        {
            'xmlid': 'ir_cron_esb_export_product_price',
            'nextcall': day_first_export + ' ' + '02:30:00'
        },
        {
            'xmlid': 'ir_cron_esb_export_special_promotion',
            'nextcall': day_first_export + ' ' + '03:00:00'
        },
        {
            'xmlid': 'ir_cron_esb_export_buy_x_get_y',
            'nextcall': day_first_export + ' ' + '03:15:00'
        },
        {
            'xmlid': 'ir_cron_esb_export_stock_update',
            'nextcall': day_first_export + ' ' + '03:30:00'
        },
        {
            'xmlid': 'ir_cron_esb_export_document_zip_morning',
            'nextcall': day_first_export + ' ' + '05:00:00'
        },
        {
            'xmlid': 'ir_cron_esb_export_document_zip_afternoon',
            'nextcall': day_first_export + ' ' + '14:00:00'
        },
    ]


@anthem.log
def update_next_call(ctx):
    """Update the next call for all export."""
    for cron_job in all_cron:
        j = ctx.env.ref(module + '.' + cron_job['xmlid'])
        j.nextcall = cron_job['nextcall']


@anthem.log
def activate_all(ctx):
    """Active all ESB export cron job."""
    for cron_job in all_cron:
        j = ctx.env.ref(module + '.' + cron_job['xmlid'])
        j.active = True


@anthem.log
def deactivate_all(ctx):
    """Deactive all ESB export cron job."""
    for cron_job in all_cron:
        j = ctx.env.ref(module + '.' + cron_job['xmlid'])
        j.active = False


@anthem.log
def set_stock_last_export(ctx):
    """Set the stock timestamp."""
    stock_ts = ctx.env.ref('connector_esb.esb_timestamp_stock_update')
    stock_ts.last_export = stock_last_export


@anthem.log
def main(ctx):
    """Activate and set up cron esb export.

    To avoid any problem during the migration the cron jobs running
    the export to the ESB are disabled until the data migration is
    finished.
    Calling this will activate them all

    """
    update_next_call(ctx)
    set_stock_last_export(ctx)
    activate_all(ctx)
