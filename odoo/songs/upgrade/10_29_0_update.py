
# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from pkg_resources import resource_stream

import anthem
from anthem.lyrics.loaders import load_csv_stream
from anthem.lyrics.records import add_xmlid

from ..common import req


@anthem.log
def set_xid_legal_entity(ctx):
    """An xml id is missing on a legal entity"""
    xid = '__setup__.legal_entity_12'
    entity = ctx.env.ref(xid, raise_if_not_found=False)
    if entity:
        return
    entity = ctx.env['legal.entity'].search([('name', '=', 'CAB VET')])
    if not entity:
        return
    add_xmlid(ctx, entity, xid)


@anthem.log
def import_customers(ctx):
    # Directly called as post_full in migration.yml
    load_ctx = ctx.env.context.copy()
    load_ctx.update({'tracking_disable': True})
    Partner = ctx.env['res.partner'].with_context(load_ctx)

    file_list = [
        'customer.change-active-call_name-email.csv',
        'customer.change-active-call_name-pharmacist_id.csv',
        'customer.change-active-call_name.csv',
        'customer.change-active-property_payment_term_id-call_name-customer_payment_mode_id.csv',  # noqa
        'customer.change-active.csv',
        'customer.change-alcyon_category_id.csv',
        'customer.change-call_name-customer_payment_mode_id-name.csv',
        'customer.change-call_name-name.csv',
        'customer.change-call_name.csv',
        'customer.change-category_id.csv',
        'customer.change-city.csv',
        'customer.change-comment-fax-name-mobile-phone-street-suite-email-vet_depot_number.csv',  # noqa
        'customer.change-comment-phone.csv',
        'customer.change-comment.csv',
        'customer.change-customer_payment_mode_id-name.csv',
        'customer.change-discount_pricelist_id.csv',
        'customer.change-email.csv',
        'customer.change-fax.csv',
        'customer.change-help_with_fee-discount_pricelist_id.csv',
        'customer.change-help_with_fee.csv',
        'customer.change-mobile-phone.csv',
        'customer.change-name-street-category_id-suite-title-email-vet_depot_number.csv',  # noqa
        'customer.change-pharmacist_id.csv',
        'customer.change-property_payment_term_id-customer_payment_mode_id.csv',  # noqa
        'customer.change-property_payment_term_id-pharmacist_id.csv',
        'customer.change-property_payment_term_id.csv',
        'customer.change-supplier_promotion_sale_allowed-discount_pricelist_id.csv',  # noqa
        'customer.change-title-company_type-legal_entity_id-is_company.csv',
        'customer.change-user_id.csv',
        'customer.change-vet_depot_number-alcyon_category_id.csv',
        'customer.change-vet_subscription_number-alcyon_category_id-category_id.csv',  # noqa
        'customer.change-vet_subscription_number.csv',
        'customer.new.csv',
    ]

    for f in file_list:
        base_path = 'data/update/10.29.0/'
        f_path = base_path + f
        with ctx.log(u"Importing customer file: %s" % f_path):
            content = resource_stream(req, f_path)
            load_csv_stream(ctx, Partner, content, delimiter=',')
