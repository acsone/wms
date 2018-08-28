# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem


@anthem.log
def remove_pickingtype_humain(ctx):
    picking_type = ctx.env.ref(
        '__setup__.stock_picking_type_humain',
        raise_if_not_found=False
    )
    if picking_type:
        picking_type.unlink()
    location = ctx.env.ref(
        '__setup__.stock_location_pharma',
        raise_if_not_found=False
    )
    if location:
        location.unlink()


@anthem.log
def post(ctx):
    """ POST 10.23.3 """
    remove_pickingtype_humain(ctx)
