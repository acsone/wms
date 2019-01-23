# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem


@anthem.log
def configure_alcyon_delivery_method(ctx):
    """ Change parameters for alcyon delivery.

    Change the parameter for the carrier
    And the product that is used on a sale order for shipping cost.
    """
    delivery_cost_product = ctx.env.ref(
        '__setup__.deliver_carrier_alcyon_product_product'
    )
    delivery_cost_product.invoice_policy = 'order'
    delivery_cost_product.name = 'Shipping cost'
    delivery_cost_product.with_context(
        {'lang': 'fr_BE'}
    ).name = 'Frais de livraison'


@anthem.log
def post(ctx):
    """ POST 10.27.4 """
    configure_alcyon_delivery_method(ctx)
