# -*- coding: utf-8 -*-
# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem


@anthem.log
def remove_spaces_from_cnk_codes(ctx):
    """Removing spaces from product.template field cnk_code"""
    products = ctx.env['product.template'].search([])
    n = 0
    for product in products:
        cnk_code = product['cnk_code']
        if cnk_code:
            product.write({'cnk_code': cnk_code.replace(' ', '')})
            n += 1
    ctx.log_line("Processed {} product templates".format(n))


@anthem.log
def post(ctx):
    """Applying update 10.0.1.43.0 POST"""
    remove_spaces_from_cnk_codes(ctx)
