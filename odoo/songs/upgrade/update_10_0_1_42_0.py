# -*- coding: utf-8 -*-
# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem
from anthem.lyrics.records import create_or_update


@anthem.log
def set_cron_args(ctx):
    """Set args to cron """
    create_or_update(
        ctx,
        'ir.cron',
        'specific_purchase.generate_procurement_order',
        {'args': "('use_new_cursor=True',)"},
    )


@anthem.log
def pre(ctx):
    """ PRE upgrade 10.0.1.42.0 """
    set_cron_args(ctx)
