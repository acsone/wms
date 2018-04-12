# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem


@anthem.log
def post(ctx):
    remove_implied_groups(ctx)


@anthem.log
def remove_implied_groups(ctx):
    """ Remove implied groups """
    group_inventory = ctx.env.ref('stock.group_stock_user')
    ctx.env.ref('purchase.group_purchase_user').write({
        'implied_ids': [(3, group_inventory.id)],
    })
    ctx.env.ref('sales_team.group_sale_salesman').write({
        'implied_ids': [(3, group_inventory.id)],
    })
