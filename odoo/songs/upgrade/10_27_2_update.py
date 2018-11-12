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
def set_max_records_on_stock_export(ctx):
    """Set the maximum of records on stock export.

    The stock export is using a web service on the ESB. If too many
    records are exported it will fail. Here we set the maximum of records
    exported to 500.
    It is just a guess from past test of this export.

    """
    timestamp = ctx.env.ref('connector_esb.esb_timestamp_stock_update')
    timestamp.max_records = 500


@anthem.log
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
    remove_customer_supplier_balance(ctx)


@anthem.log
def post(ctx):
    """ POST 10.27.2 """
    switch_helpdesk_ticket_reason_noupdate(ctx, noupdate=True)
    reset_default_value_for_supplierinfo(ctx)
    set_max_records_on_stock_export(ctx)
