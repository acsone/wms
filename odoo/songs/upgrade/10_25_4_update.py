# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem


@anthem.log
def set_cron_to_noupdate(ctx):
    """Set pesky cron to noupdate"""
    sql = ("UPDATE ir_model_data"
           "    SET noupdate = true"
           "    WHERE name = 'generate_procurement_order' AND"
           "          module = 'specific_purchase' AND"
           "          model='ir.cron'")
    ctx.env.cr.execute(sql)


@anthem.log
def pre(ctx):
    """ PRE 10.25.4 """
    set_cron_to_noupdate(ctx)
