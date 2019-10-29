# -*- coding: utf-8 -*-
# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem

from odoo.tools import float_compare


@anthem.log
def fix_sale_order_line_wrong_discount(ctx):
    """ALCYN-2292: fix the price subtotal on sale order lines"""
    lines = ctx.env['sale.order.line'].search(
        [
            ('create_date', '>=', '2019-09-01 00:00:00'),
            '|',
            ('discount2', '>', 0),
            ('discount3', '>', 0),
        ]
    )
    line_ids = []
    for line in lines:
        disc = (1 - line.discount2 / 100.0) * (1 - line.discount3 / 100.0)
        if 0 != float_compare(
            line.price_subtotal,
            line.price_unit * line.product_uom_qty * disc,
            2,
        ):
            line.price_unit = line.price_unit  # force recompute price subtotal
            line_ids.append(line.id)
    lines = ctx.env['sale.order.line'].browse(line_ids)
    orders = lines.mapped('order_id')
    for order in orders:
        order.message_post(
            body='Sale updated:\nfix discounts not taken '
            'into account on some lines when it was saved',
            content_subtype='plaintext',
        )


@anthem.log
def post(ctx):
    """Applying update 10.0.1.44.3 POST"""
    fix_sale_order_line_wrong_discount(ctx)
