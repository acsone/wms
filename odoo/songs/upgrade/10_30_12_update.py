# -*- coding: utf-8 -*-
# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem


@anthem.log
def propagate_sale_carrier(ctx):
    sql = """
    UPDATE procurement_group g
    SET carrier_id = o.carrier_id
    FROM sale_order o
    WHERE o.carrier_id IS NOT NULL
    AND g.id = o.procurement_group_id
    """
    ctx.env.cr.execute(sql)


@anthem.log
def post(ctx):
    """POST 10.30.12"""
    propagate_sale_carrier(ctx)
