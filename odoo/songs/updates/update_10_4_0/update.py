# -*- coding: utf-8 -*-
# Author: Julien Coux
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import anthem


@anthem.log
def change_default_lead_time(ctx):
    """
    Change the default lead time to 0 day
    :param ctx:
    :return:
    """
    ctx.env['ir.config_parameter'].set_param('purchase.lead_time', '0')


@anthem.log
def main(ctx):
    """ Update 10.4.0 """
    change_default_lead_time(ctx)
