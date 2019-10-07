# -*- coding: utf-8 -*-
# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem


@anthem.log
def set_stock_location_excluded_from_usable_qty(ctx):
    """Set stock location excluded from immediately available quantity."""
    location = ctx.env['stock.location'].search([('kind', '=', 'parking')])
    location.write({'exclude_from_immediately_usable_qty': True})


@anthem.log
def post(ctx):
    """Applying update 10.0.1.44.0 POST"""
    set_stock_location_excluded_from_usable_qty(ctx)
