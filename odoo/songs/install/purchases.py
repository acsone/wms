# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from pkg_resources import resource_stream

import anthem
from anthem.lyrics.records import create_or_update
from anthem.lyrics.loaders import load_csv_stream

from ..common import req


@anthem.log
def settings(ctx):
    """ Configure the Purchases Settings.
    """
    ctx.env['purchase.config.settings'].create({
        'group_manage_vendor_price': 1,
        'turnover_delay': 12,
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


@anthem.log()
def set_abc_rate(ctx):
    """
    Set ABC rates (80, 95 and 100 percent)
    :param ctx:
    :return:
    """
    rates = [
        ('__setup__.abc_rate_80', 'A', 80),
        ('__setup__.abc_rate_95', 'B', 95),
        ('__setup__.abc_rate_100', 'C', 100),
    ]
    for xmlid, code, rate in rates:
        create_or_update(ctx, 'activity.based.costing', xmlid, {
            'code': code,
            'rate': rate,
        })


@anthem.log()
def set_business_unit(ctx):
    """
    Set business unit and recompute ABC code
    :param ctx:
    :return:
    """

    business_units = ctx.env.ref('specific_data.product_categ_materiel')
    business_units |= ctx.env.ref('specific_data.product_categ_ali')
    business_units |= ctx.env.ref('specific_data.product_categ_medoc')
    business_units |= ctx.env.ref('specific_data.product_categ_finance')
    business_units.write({'is_business_unit': True})

    ctx.env['product.product'].update_abc_code()


@anthem.log
def main(ctx):
    """ Configuring purchases """
    settings(ctx)
    change_default_lead_time(ctx)
    import_bank_holidays(ctx)
    set_abc_rate(ctx)
    set_business_unit(ctx)
