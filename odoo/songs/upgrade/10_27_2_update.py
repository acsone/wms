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
<<<<<<< 56f0503cc642dc367778d49e94cccbd7006bc64b
def switch_helpdesk_ticket_reason_noupdate(ctx, noupdate):
    model_datas = ctx.env['ir.model.data'].search([
        ('model', '=', 'helpdesk.ticket.reason'),
        ('module', '=', 'specific_helpdesk')
    ])
    model_datas.write({'noupdate': noupdate})


@anthem.log
def reset_default_value_for_supplierinfo(ctx):
    """ Reset the default value for sale minimum quantity on supplier info """

    ctx.env.cr.execute("UPDATE product_supplierinfo "
                       "SET min_qty_sale = 0 WHERE min_qty_sale = 1;")


@anthem.log
def pre(ctx):
    """ PRE 10.27.2 """
    switch_helpdesk_ticket_reason_noupdate(ctx, noupdate=False)


@anthem.log
def post(ctx):
=======
def pre(ctx):
>>>>>>> ALCYN-1614: Update the balance for customers and suppliers
    """ POST 10.27.2 """
    remove_customer_supplier_balance(ctx)
    switch_helpdesk_ticket_reason_noupdate(ctx, noupdate=True)
    reset_default_value_for_supplierinfo(ctx)
