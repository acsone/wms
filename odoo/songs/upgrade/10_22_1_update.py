# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem


@anthem.log
def remove_taxes_on_ser_705008_products(ctx):
    """ Remove taxes on SER-705008 accounting products """
    products = ctx.env.ref('__setup__.product_SER-705008-1')
    products |= ctx.env.ref('__setup__.product_SER-705008-2')

    products.write({
        'taxes_id': [(6, 0, [])],
        'supplier_taxes_id': [(6, 0, [])]
    })


@anthem.log
def post(ctx):
    """ Applying post 10.22.1 """
    remove_taxes_on_ser_705008_products(ctx)
