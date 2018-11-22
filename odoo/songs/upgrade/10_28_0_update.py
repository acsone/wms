# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from pkg_resources import resource_stream

from anthem.lyrics.loaders import load_csv_stream

from ..common import req


def import_customers(ctx):
    # Directly called as post_full in migration.yml
    load_ctx = ctx.env.context.copy()
    load_ctx.update({'tracking_disable': True})
    Partner = ctx.env['res.partner'].with_context(load_ctx)

    file_list = [
        'customer.change-active-call_name.csv',
        'customer.change-active-call_name-user_id.csv',
        'customer.change-active-city-call_name-street-zip.csv',
        'customer.change-active.csv',
        'customer.change-call_name.csv',
        'customer.change-call_name-customer_payment_mode_id-name.csv',
        'customer.change-call_name-name.csv',
        'customer.change-call_name-name-vet_subscription_number.csv',
        'customer.change-city.csv',
        'customer.change-city-street.csv',
        'customer.change-city-street-zip.csv',
        'customer.change-comment-city-street-zip.csv',
        'customer.change-comment.csv',
        'customer.change-comment-discount_pricelist_id.csv',
        'customer.change-comment-mobile.csv',
        'customer.change-comment-street.csv',
        'customer.change-discount_pricelist_id.csv',
        'customer.change-discount_pricelist_id-customer_payment_mode_id.csv',
        'customer.change-email.csv',
        'customer.change-help_with_fee.csv',
        'customer.change-help_with_fee-discount_pricelist_id.csv',
        'customer.change-invoice_sending_method.csv',
        'customer.change-invoice_sending_method-discount_pricelist_id.csv',
        'customer.change-invoice_sending_method-email.csv',
        'customer.change-is_price_on_labels.csv',
        'customer.change-mobile.csv',
        'customer.change-name-company_type-legal_entity_id-call_name-suite-is_company.csv',  # noqa
        'customer.change-name-vet_subscription_number-mobile-call_name-vet_depot_number-category_id-email-vat.csv',  # noqa
        'customer.change-property_delivery_carrier_id.csv',
        'customer.change-property_payment_term_id.csv',
        'customer.change-street.csv',
        'customer.change-suite.csv',
        'customer.change-suite-email-name.csv',
        'customer.change-supplier_promotion_sale_allowed-discount_pricelist_id.csv',  # noqa
        'customer.change-supplier_promotion_sale_allowed-discount_pricelist_id-street.csv',  # noqa
        'customer.change-vat.csv',
        'customer.change-vet_depot_number.csv',
        'customer.change-vet_depot_number-vat.csv',
        'customer.change-vet_subscription_number.csv',
        'customer.new.csv',
    ]

    for f in file_list:
        base_path = 'data/update/10.28.0/'
        f_path = base_path + f
        with ctx.log(u"Importing customer file: %s" % f_path):
            content = resource_stream(req, f_path)
            load_csv_stream(ctx, Partner, content, delimiter=',')
