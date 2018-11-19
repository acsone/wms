# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem
from anthem.lyrics.records import add_xmlid


@anthem.log
def add_xmlid_users(ctx):
    ctx.env.cr.execute("""
        SELECT res_id from ir_model_data
        WHERE model='res.users' AND module!='__setup__';
    """)
    noupdate_users_ids = ctx.env.cr.fetchall()
    users = ctx.env['res.users'].with_context(
        active_test=False).search([('id', 'not in', noupdate_users_ids)])
    for user in users:
        add_xmlid(
            ctx, user,
            '__setup__.res_user_' + user.login,
            noupdate=False
        )


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


def post(ctx):
    """ POST 10.28.1 """
    add_xmlid_users(ctx)
    remove_customer_supplier_balance(ctx)
