# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem
from anthem.lyrics.modules import uninstall


@anthem.log
def drop_round_instance_sql_constrain(ctx):
    """ Drop a contrain removed in the python code """
    drop_constraint_query = """
    ALTER TABLE round_instance_customer
    DROP CONSTRAINT IF EXISTS round_instance_customer_unique_instance_partner;
    """
    ctx.env.cr.execute(drop_constraint_query)


@anthem.log
def uninstall_modules(ctx):
    """ Uninstall modules """
    uninstall(
        ctx,
        [
            'stock_picking_invoice_link',
        ]
    )


@anthem.log
def pre(ctx):
    """ PRE 10.25.2 """
    drop_round_instance_sql_constrain(ctx)


@anthem.log
def post(ctx):
    """ Post 10.25.3 """
    uninstall_modules(ctx)
