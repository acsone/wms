# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem


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
