# -*- coding: utf-8 -*-
# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import anthem


@anthem.log
def set_operators_as_portal(ctx):
    operators = (
        ctx.env['res.users']
        .with_context(active_test=False)
        .search([('operator_code', '!=', False)])
    )
    portal_group = ctx.env.ref('base.group_portal')
    operators.write({'groups_id': [(5,), (4, portal_group.id)]})


@anthem.log
def post(ctx):
    """Applying update 10.0.1.38.0"""
    set_operators_as_portal(ctx)
