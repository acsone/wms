# -*- coding: utf-8 -*-
# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


import anthem


@anthem.log
def reload_translation(ctx):
    """ update translation """
    ctx.env['ir.module.module'].with_context(overwrite=True).search(
        [('name', '=', 'specific_report')]
    ).update_translations()


@anthem.log
def record_returned_qty(ctx):
    """populate the returned qty field on SO lines"""
    returns = ctx.env['stock.move'].search(
        [('origin_returned_move_id', '!=', False),
         ('state', '=', 'done'),
         ]
    )
    for move in returns.filtered('order_line_id'):
        move.order_line_id.product_qty_returned += move.product_uom_qty


@anthem.log
def post(ctx):
    reload_translation(ctx)
