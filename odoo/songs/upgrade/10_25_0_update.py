# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
import anthem


@anthem.log
def activate_group_shipping(ctx):
    """ Activate group shipping """
    ctx.env.ref('stock.picking_type_out').groupbypartner = True


@anthem.log
def pre(ctx):
    """ PRE 10.25.0 """
    activate_group_shipping(ctx)
