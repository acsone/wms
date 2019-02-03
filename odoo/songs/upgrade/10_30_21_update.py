# -*- coding: utf-8 -*-
# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem


@anthem.log
def post(ctx):
    """POST 10.30.21"""
    fix_additional_product_move_name(ctx)
    create_fix_delivery_picking_type(ctx)


@anthem.log
def create_fix_delivery_picking_type(ctx):
    """create a new picking type to be used for the pickings to fix.

    use self.env.ref('__setup__.stock_picking_type_fix_ship') to acces it.
    """
    ptype = ctx.env.ref(
        '__setup__.stock_picking_type_fix_ship',
        raise_if_not_found=False
    )
    if ptype:  # make sure script is idempotent
        return ptype
    ship = ctx.env['stock.picking.type'].browse(4)  # shipping picking type
    ptype = ship.copy({'name': 'Correction pb livraison'})
    ctx.env['ir.model.data'].create(
        {'name': 'stock_picking_type_fix_ship',
         'module': '__setup__',
         'model': 'stock.picking.type',
         'res_id': ptype.id,
         }
    )
    return ptype


@anthem.log
def fix_additional_product_move_name(ctx):
    """clarify the description of the stock moves created as part of a promotion
    (buy some product, get another for free)
    """
    products_with_additional = ctx.env['product.product'].search(
        [('additional_product_id', '!=', False)]
    )
    additional_products = products_with_additional.mapped(
        'additional_product_id'
    )
    map = {}  # bonus product -> list of products giving this bonus
    for p in products_with_additional:
        map.setdefault(p.additional_product_id, []).append(p)
    moves = ctx.env['stock.move'].search(
        [('product_id', 'in', additional_products.ids),
         ('name', 'not like', 'INV:%'),
         ('name', 'not like', 'ADDITIONAL PRODUCT:%'),
         ]
    )
    renamed = []
    new_name = 'ADDITIONAL PRODUCT: %s (FROM %s)'
    for move in moves:
        for p in map[move.product_id]:
            if move.name == p.display_name:
                move.name = new_name % (move.product_id.display_name,
                                        p.display_name)
                renamed.append(move.id)
                break
    return ctx.env['stock.move'].browse(renamed)
