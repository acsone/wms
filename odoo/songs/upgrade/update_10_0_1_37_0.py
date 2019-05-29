# -*- coding: utf-8 -*-
# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import anthem

from odoo.tools import float_compare


@anthem.log
def fix_product_cost(ctx):
    """fix the last cost price for products for which it was wrongly computed

    because the purchase price changed after purchase confirmation"""
    moves = ctx.env['stock.move'].search([('purchase_line_id', '!=', False)])
    product_ids = set()
    for move in moves:
        product = move.product_id
        if product.id in product_ids:
            continue  # already processed that one
        expected_price_unit = (
            move.purchase_line_id._get_stock_move_price_unit()
        )
        if float_compare(move.price_unit, expected_price_unit, 2) == 0:
            continue  # price is same, move on
        product_ids.add(product.id)
        # product found here have at least one stock move with a price_unit
        # different from the linked purchase line price_unit -> we do something
        # about it
        last_move = ctx.env['stock.move'].search(
            [
                ('product_id', '=', product.id),
                ('state', '=', 'done'),
                ('purchase_line_id', '!=', False),
            ],
            order='date desc',
            limit=1,
        )
        if last_move:
            cost_price = (
                last_move.purchase_line_id._get_stock_move_price_unit()
            )
            if float_compare(product.standard_price, cost_price, 2) != 0:
                product.message_post(
                    'Fixed cost price %.2f -> %.2f'
                    % (product.standard_price, cost_price),
                    subject='Fix average price',
                    content_subtype='plaintext',
                )
                last_historic_price = ctx.env['product.price.history'].search(
                    [('product_id', '=', product.id)],
                    order='datetime desc',
                    limit=1,
                )
                last_historic_price.cost = cost_price
                # Following line creates an additional entry in
                # product.price.history dated from today. Should not be a
                # problem.
                product.standard_price = cost_price
            else:
                # no update needed as average price is the one we would have set
                pass


@anthem.log
def post(ctx):
    """Applying update 10.0.1.37.0"""
    fix_product_cost(ctx)
