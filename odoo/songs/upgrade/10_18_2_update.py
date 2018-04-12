# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from pkg_resources import resource_stream
import anthem
from anthem.lyrics.loaders import load_csv_stream
from ..common import req


@anthem.log
def pre(ctx):
    remove_helpdesk_team(ctx)
    reload_delivery_carrier(ctx)


@anthem.log
def post(ctx):
    remove_implied_groups(ctx)


@anthem.log
def remove_helpdesk_team(ctx):
    """Remove preconfigured helpdesk team."""
    r_id = ctx.env.ref('helpdesk.helpdesk_team1', raise_if_not_found=False)
    if r_id:
        r_id.unlink()


@anthem.log
def reload_delivery_carrier(ctx):
    """ Reload the delivery carrier csv, some esb_ref have changed"""
    load_ctx = ctx.env.context.copy()
    load_ctx.update({'tracking_disable': True})
    Carrier = ctx.env['delivery.carrier'].with_context(load_ctx)
    content = resource_stream(req, 'data/install/delivery.carrier.csv')
    load_csv_stream(ctx, Carrier, content, delimiter=',')


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
