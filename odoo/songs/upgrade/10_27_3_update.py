# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem


@anthem.log
def drop_ir_cron_connector_esb_export_documents(ctx):
    rec = ctx.env.ref('connector_esb.ir_cron_esb_export_document_zip',
                      raise_if_not_found=False)
    if rec:
        rec.unlink()


@anthem.log
def pre(ctx):
    """ PRE 10.27.3 """
    drop_ir_cron_connector_esb_export_documents(ctx)


@anthem.log
def configure_alcyon_delivery_method(ctx):
    """ Change parameters for alcyon delivery.

    Change the parameter for the carrier
    And the product that is used on a sale order for shipping cost.
    """
    alcyon_delivery = ctx.env.ref('__setup__.deliver_carrier_alcyon')
    alcyon_delivery.fixed_price = 8.5
    alcyon_delivery.free_if_more_than = True
    alcyon_delivery.amount = 125
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
    """ POST 10.27.3 """
    configure_alcyon_delivery_method(ctx)
