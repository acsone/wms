# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem
from anthem.lyrics.modules import uninstall


@anthem.log
def post(ctx):
    uninstall_module_account_sepa(ctx)
    restore_min_max(ctx)


@anthem.log
def uninstall_module_account_sepa(ctx):
    """ Uninstall the module account_sepa """

    # Uninstall the module account_sepa
    uninstall(ctx, ['account_sepa'])


@anthem.log
def restore_min_max(ctx):
    """ Restore Min/Max on product """

    orderpoints = ctx.env['stock.warehouse.orderpoint'].search([])
    for orderpoint in orderpoints:
        product = orderpoint.product_id
        product.with_context(disable_constrains_orderpoint=True).write({
            'orderpoint_min': orderpoint.product_min_qty,
            'orderpoint_max': orderpoint.product_max_qty,
            'orderpoint_qty_multiple': orderpoint.qty_multiple,
        })
