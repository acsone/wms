# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import os
from pkg_resources import resource_stream
import anthem
from anthem.lyrics.loaders import load_csv_stream
from ..common import req


@anthem.log
def change_admin_language(ctx):
    """ Changing admin language """
    ctx.env.ref('base.user_root').lang = 'fr_BE'


@anthem.log
def admin_user_password(ctx):
    if os.getenv('RUNNING_ENV') in ('dev', ):
        ctx.log_line('RUNNING_ENV=dev => nothing to do here.')
        return
    # password for the test server,
    # the password must be changed in production
    ctx.env.user.password_crypt = (
        '$pbkdf2-sha512$12000$cC4FIIRwjvE.p1SKcY5xTg$DkQBZfffiE18idabgyhey'
        'UBLm9inCLxoi.UWKPFWO.E32HEpwRjz4Ps2z3/r0eSDFGL1HZXTXmNjD103jfAHYg'
    )


@anthem.log
def set_implied_groups(ctx):
    """ Define some implied groups """
    group_printing = ctx.env.ref('base_report_to_printer.printing_group_user')
    group_helpdesk = ctx.env.ref('helpdesk.group_helpdesk_user')
    ctx.env.ref('base.group_user').write({
        'implied_ids': [(4, group_printing.id), (4, group_helpdesk.id)]
    })

    group_payment = ctx.env.ref('account_payment_order.group_account_payment')
    ctx.env.ref('account.group_account_user').write({
        'implied_ids': [(4, group_payment.id)],
    })

    # Set
    group_inventory = ctx.env.ref('stock.group_stock_user')
    ctx.env.ref('purchase.group_purchase_user').write({
        'implied_ids': [(4, group_inventory.id)],
    })
    ctx.env.ref('sales_team.group_sale_salesman').write({
        'implied_ids': [(4, group_inventory.id)],
    })


@anthem.log
def import_users(ctx):
    """ Import users """
    content = resource_stream(req, 'data/install/res.users.csv')
    load_csv_stream(ctx, 'res.users', content, delimiter=',')


@anthem.log
def esb_user_password(ctx):
    """ Change ESB User password """
    if os.getenv('RUNNING_ENV') in ('dev', ):
        ctx.log_line('RUNNING_ENV=dev => nothing to do here.')
        return
    user = ctx.env.ref('__setup__.res_user_wso2')
    user.password_crypt = (
        '$pbkdf2-sha512$19000$VmotpRQixBgDwBjDGEMoxQ$xFRJGwx9lYflbRdfRQbgw'
        'rXetTOkADQokLO3FWLOhaXhR0TRx.nqrm4gOOQIlmF5ppL3oZaCAYj3fRLfT/Fjmg'
    )


@anthem.log
def main(ctx):
    """ Configuring products """
    change_admin_language(ctx)
    admin_user_password(ctx)
    set_implied_groups(ctx)
    import_users(ctx)
    esb_user_password(ctx)
