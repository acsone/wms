# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem


@anthem.log
def remove_pickingtype_humain(ctx):
    picking_type_id = ctx.env.ref('__setup__.stock_picking_type_humain')
    picking_type_id.unlink()
    location_id = ctx.env.ref('__setup__.stock_location_pharma')
    location_id.unlink()


@anthem.log
def post(ctx):
    """ POST 10.23.3 """
    remove_pickingtype_humain(ctx)
