# -*- coding: utf-8 -*-
# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem


@anthem.log
def reload_translation(ctx):
    """ update translation """
    modules = [
        'account_invoice_sent',
        'account_move_productcateg',
        'cash_on_delivery',
        'delivery_rounds',
        'delivery_rounds_refill',
        'l10n_be_bba_fix',
        'partner_schedule',
        'procurement_sale',
        'purchase_prepaid',
        'sale_cancel_remaining',
        'sale_confirm_background',
        'specific_account',
        'specific_barcode',
        'specific_helpdesk',
        'specific_report',
        'specific_shipping_costs',
        'stock_barcode_fix',
        'stock_delivery_note',
        'stock_grn',
        'stock_groupbypartner',
        'stock_lot_update',
        'stock_lot_update',
        'stock_picking_backorder',
        'stock_picking_fillwithstock',
        'stock_picking_sequence',
        'stock_picking_subcode',
        'stock_product_bin',
        'stock_putaway_defaultfixedlocation',
        'stock_putaway_route',
        'stock_quant_bylocation',
        'stock_receive_lot',
        'stock_reception_priority',
        'stock_refill',
        'stock_unit',
        'stock_valuation',
        'web_autorefresh',
    ]
    ctx.env['ir.module.module'].with_context(overwrite=True).search(
        [('name', 'in', modules)]
    ).update_translations()


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
    reload_translation(ctx)
