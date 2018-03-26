# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem


@anthem.log
def pre(ctx):
    remove_unused_sales_team(ctx)


@anthem.log
def remove_unused_sales_team(ctx):
    """Remove unused sales team."""
    team1 = ctx.env.ref(
        '__setup__.sales_team_ecommerce',
        raise_if_not_found=False,
    )
    if team1:
        team1.unlink()
    team2 = ctx.env.ref(
        '__setup__.sales_team_ebusiness',
        raise_if_not_found=False,
    )
    if team2:
        team2.unlink()
