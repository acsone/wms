# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem


@anthem.log
def pre(ctx):
    remove_old_pesky_views(ctx)


@anthem.log
def remove_old_pesky_views(ctx):
    """The rewrite of shipping_costs caused some problems with the views."""
    sql = "DELETE FROM ir_ui_view where arch_db ~'costs_on_in'"
    ctx.env.cr.execute(sql)
