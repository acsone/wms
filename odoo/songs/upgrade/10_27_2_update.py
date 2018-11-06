# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem


@anthem.log
def remove_customer_supplier_balance(ctx):
    """ Remove customer and supplier balance """
    balance_customer = ctx.env.ref(
        '__setup__.account_move_balance_customer', raise_if_not_found=False)
    if balance_customer:
        balance_customer.unlink()

    balance_supplier = ctx.env.ref(
        '__setup__.account_move_balance_supplier', raise_if_not_found=False)
    if balance_supplier:
        balance_supplier.unlink()


@anthem.log
def post(ctx):
    """ POST 10.27.2 """
    remove_customer_supplier_balance(ctx)
