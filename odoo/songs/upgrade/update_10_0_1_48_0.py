# -*- coding: utf-8 -*-
# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem

from odoo import exceptions


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
def fix_pickings_delivery_rounds(ctx):
    fix_empty_pickings(ctx)
    call_action_done(ctx)
    move_backorders_out(ctx)


@anthem.log
def fix_empty_pickings(ctx):
    # 1. fix empty pickings with state = assigned
    empty_pickings = (
        ctx.env['stock.picking']
        .search(
            [
                ('delivery_round_id', '=', False),
                ('printed', '=', False),
                ('state', '=', 'assigned'),
                ('picking_type_id', 'in', (16, 18, 17, 4, 15)),
            ]
        )
        .with_context(tracking_disable=True)
    ).filtered(lambda r: not r.move_lines)
    empty_pickings.write({'printed': True, 'state': 'done'})


@anthem.log
def call_action_done(ctx):
    # 2. call action_done on pickings with > 1 procurement group
    ctx.env.cr.execute(
        "SELECT m.picking_id "
        "FROM stock_move m "
        "LEFT JOIN procurement_group g ON m.group_id=g.id "
        "LEFT JOIN stock_picking p on m.picking_id=p.id "
        "WHERE not p.printed AND m.state NOT IN ('cancel', 'done') "
        "GROUP BY m.picking_id "
        "HAVING COUNT(distinct g.carrier_id) > 1;"
    )
    picking_ids = [row[0] for row in ctx.env.cr.fetchall()]
    for pick in ctx.env['stock.picking'].browse(picking_ids):
        try:
            pick.action_done()
        except exceptions.UserError as exc:
            print 'failed to call action_done on %s: %s' % (pick.name, exc)


@anthem.log
def move_backorders_out(ctx):
    # 3. move backorders out of delivery rounds
    errors = []
    pickings = ctx.env['stock.picking'].search(
        [
            ('state', 'not in', ('cancel', 'done')),
            ('delivery_round_id.state', '=', 'done'),
            ('printed', '=', True),
        ]
    )
    pickings.with_context(tracking_disable=True).write({'printed': True})
    for pick in pickings:
        if pick.partner_id.is_sale_back_order_cancel:
            print pick.name, "backorder cancel"
            pick.with_context(
                no_new_picking=True, cancel_backorder=True
            )._create_backorder()
        else:
            print pick.name
            pick.with_context(no_new_picking=True)._create_backorder()
        pick.with_context(tracking_disable=True).write({'printed': False})
        try:
            pick.write({'delivery_round_customer_id': False})
        except exceptions.UserError as exc:
            print
            print 'ERROR', pick.name, exc
            print
            errors.append((pick, pick.name, str(exc)))
        return errors


@anthem.log
def post(ctx):
    recompute_delivered_qty(ctx)
    reload_translation(ctx)
