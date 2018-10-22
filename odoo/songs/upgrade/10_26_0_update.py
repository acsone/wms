# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from pkg_resources import resource_stream

import anthem
from anthem.lyrics.loaders import load_csv_stream

from ..common import req


@anthem.log
def drop_round_instance_sql_constrain(ctx):
    """ Drop a contrain removed in the python code """
    drop_constraint_query = """
    ALTER TABLE round_instance_customer
    DROP CONSTRAINT IF EXISTS round_instance_customer_unique_instance_partner;
    """
    ctx.env.cr.execute(drop_constraint_query)


def update_translations(ctx):
    modules_to_update = ['specific_product', 'specific_purchase']
    langs_to_update = ['fr_BE']

    IrModuleModule = ctx.env['ir.module.module']
    modules = IrModuleModule.search([('name', 'in', modules_to_update)])

    modules.with_context(overwrite=True).update_translations(langs_to_update)


def cleanup_delivery_demo_data(ctx):
    ctx.env.cr.execute("DELETE FROM round_instance;")
    ctx.env.cr.execute("DELETE FROM round_wizard_makeplan;")
    ctx.env.cr.execute("DELETE FROM round_itinerary_import;")
    ctx.env.cr.execute("DELETE FROM round_itinerary;")
    ctx.env.cr.execute("DELETE FROM round_template;")
    ctx.env.cr.execute("DELETE FROM round_template_version;")


@anthem.log
def post(ctx):
    """ POST 10.26.0 """
    update_translations(ctx)
    drop_round_instance_sql_constrain(ctx)


@anthem.log
def post_full(ctx):
    """ POST FULL 10.26.0 """
    cleanup_delivery_demo_data(ctx)


def import_customers(ctx):
    # Directly called as post_full in migration.yml
    load_ctx = ctx.env.context.copy()
    load_ctx.update({'tracking_disable': True})
    Partner = ctx.env['res.partner'].with_context(load_ctx)

    file_list = [
        'customer.new.csv',
        'customer.change-comment.csv',
        'customer.change-active-call_name.csv',
        'customer.change-suite-call_name-property_delivery_carrier_id-email-name.csv',  # noqa
        'customer.change-vet_depot_number.csv',
        'customer.change-email.csv',
        'customer.change-email-category_id.csv',
        'customer.change-invoice_sending_method-email.csv',
        'customer.change-street-vet_depot_number.csv',
        'customer.change-user_id.csv',
        'customer.change-call_name.csv',
        'customer.change-suite-call_name-name.csv',
        'customer.change-call_name-email-name.csv',
        'customer.change-active.csv',
        'customer.change-alcyon_category_id.csv',
        'customer.change-call_name-customer_payment_mode_id-name.csv',
        'customer.change-street.csv',
        'customer.change-help_with_fee.csv',
        'customer.change-pharmacist_id.csv',
        'customer.change-call_name-name.csv',
        'customer.change-comment-city-street.csv',
        'customer.change-alcyon_category_id-category_id.csv',
        'customer.change-active-company_type-legal_entity_id-is_company-email.csv',  # noqa
        'customer.change-suite-property_delivery_carrier_id-email-alcyon_category_id.csv',  # noqa
        'customer.change-active-call_name-user_id.csv',
        'customer.change-email-user_id.csv',
        'customer.change-invoice_sending_method.csv',
        'customer.change-comment-discount_pricelist_id.csv',
        'customer.change-comment-street-name.csv',
        'customer.change-invoice_grouping.csv',
        'customer.change-city-street-zip.csv',
        'customer.change-suite.csv',
        'customer.change-discount_pricelist_id.csv',
        'customer.change-comment-help_with_fee-street.csv',
        'customer.change-invoice_frequency.csv',
        'customer.change-comment-call_name.csv',
        'customer.change-vet_depot_number-alcyon_category_id.csv',
    ]

    for f in file_list:
        base_path = 'data/update/10.26.0/'
        f_path = base_path + f
        with ctx.log(u"Importing customer file: %s" % f_path):
            content = resource_stream(req, f_path)
            load_csv_stream(ctx, Partner, content, delimiter=',')
