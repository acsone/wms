# -*- coding: utf-8 -*-
# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem


@anthem.log
def set_default_carrier_id_on_sale_order(ctx):
    """Set a default value for the carrier id on sale order."""
    ctx.env['ir.values'].set_default(
        'sale.order',
        'carrier_id',
        ctx.env.ref('__setup__.deliver_carrier_alcyon').id
    )


@anthem.log
def post(ctx):
    set_default_carrier_id_on_sale_order(ctx)
