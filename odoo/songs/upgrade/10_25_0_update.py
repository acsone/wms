# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from pkg_resources import resource_stream

import anthem
from anthem.lyrics.loaders import load_csv_stream

from ..common import req


@anthem.log
def activate_group_shipping(ctx):
    """ Activate group shipping """
    ctx.env.ref('stock.picking_type_out').groupbypartner = True


@anthem.log
def pre(ctx):
    """ PRE 10.25.0 """
    activate_group_shipping(ctx)


@anthem.log
def import_customers(ctx):
    load_ctx = ctx.env.context.copy()
    load_ctx.update({'tracking_disable': True})
    Partner = ctx.env['res.partner'].with_context(load_ctx)

    file_list = [
        'customer.new.csv',
        'customer.change-help_with_fee.csv',
        'customer.change-vet_depot_number.csv',
        'customer.change-comment.csv',
        'customer.change-help_with_fee-active-discount_pricelist_id-call_name.csv',  # noqa
        'customer.change-alcyon_category_id.csv',
        'customer.change-active-is_sale_back_order_accepted-call_name-customer_payment_mode_id.csv',  # noqa
        'customer.change-active-call_name.csv',
        'customer.change-help_with_fee-active-street-call_name.csv',
        'customer.change-suite-legal_entity_id-name.csv',
        'customer.change-discount_pricelist_id.csv',
        'customer.change-comment-street.csv',
        'customer.change-vet_subscription_number.csv',
        'customer.change-city-street-zip-suite.csv',
        'customer.change-call_name.csv',
        'customer.change-is_price_on_labels.csv',
        'customer.change-call_name-customer_payment_mode_id-name.csv',
        'customer.change-comment-city-street-vet_depot_number-zip.csv',
        'customer.change-mobile.csv',
        'customer.change-city-street-zip.csv',
        'customer.change-mobile-phone.csv',
        'customer.change-customer_payment_mode_id-name.csv',
    ]

    for f in file_list:
        base_path = 'data/update/10.25.0/'
        f_path = base_path + f
        with ctx.log(u"Importing customer file: %s" % f_path):
            content = resource_stream(req, f_path)
            load_csv_stream(ctx, Partner, content, delimiter=',')
