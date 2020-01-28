# -*- coding: utf-8 -*-
# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem


@anthem.log
def recompute_delivered_qty(ctx):

    orders_lines = ctx.env['sale.order.line'].search(
        [('order_id.is_consignment', '=', True)]
    )
    for sol in orders_lines:
        sol.qty_delivered = sol._get_delivered_qty()


@anthem.log
def post(ctx):
    recompute_delivered_qty(ctx)
