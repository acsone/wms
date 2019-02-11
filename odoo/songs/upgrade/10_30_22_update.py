# -*- coding: utf-8 -*-
# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


import anthem


@anthem.log
def configure_stock_picking_type(ctx):
    picking_types = (
        ctx.env.ref('stock.picking_type_out') |
        ctx.env.ref('__setup__.picking_type_in_return') |
        ctx.env.ref('__setup__.stock_picking_type_fix_ship')
    )
    picking_types.write({
         'create_invoice_on_transfer': True,
    })


@anthem.log
def generate_missed_draft_invoices_on_returns(ctx):
    sales = ctx.env['sale.order'].search([
        ('invoice_status', '=', 'to invoice'),
        ('partner_invoice_id.invoice_grouping', '=', 'by_delivery')]
    )
    for sale in sales:
        has_missed_picking = any(
            picking.picking_type_id.create_invoice_on_transfer
            and picking.state == 'done'
            for picking in sale.picking_ids
        )
        if not has_missed_picking:
            continue
        sale.with_delay()._job_create_draft_invoice()


@anthem.log
def reload_translation(ctx):
    """ update translation """
    ctx.env['ir.module.module'].with_context(overwrite=True).search(
        [('name', '=', 'specific_report')]
    ).update_translations()


@anthem.log
def post(ctx):
    configure_stock_picking_type(ctx)
    generate_missed_draft_invoices_on_returns(ctx)
    reload_translation(ctx)
