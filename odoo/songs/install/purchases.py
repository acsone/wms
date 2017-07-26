# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from pkg_resources import resource_stream

import anthem
from anthem.lyrics.loaders import load_csv_stream

from ..common import req


@anthem.log
def settings(ctx):
    """ Configure the Purchases Settings.
    """
    ctx.env['purchase.config.settings'].create({
        'group_manage_vendor_price': 1,
    }).execute()


@anthem.log
def change_default_lead_time(ctx):
    """
    Change the default lead time to 0 day
    :param ctx:
    :return:
    """
    ctx.env['ir.config_parameter'].set_param('purchase.lead_time', '0')


@anthem.log
def import_bank_holidays(ctx):
    """ Importing account analytic account """
    content = resource_stream(req, 'data/install/bank.holiday.csv')
    load_csv_stream(ctx, 'bank.holiday', content, delimiter=',')


@anthem.log
def main(ctx):
    """ Configuring purchases """
    settings(ctx)
    change_default_lead_time(ctx)
    import_bank_holidays(ctx)
