# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem


@anthem.log
def pre(ctx):
    remove_refs_on_addresses(ctx)


@anthem.log
def remove_refs_on_addresses(ctx):
    """Remove refs on res.partner which are delivery addresses"""
    query = "UPDATE res_partner SET ref = NULL  WHERE ref ~ 'delivery_'"
    ctx.env.cr.execute(query)
