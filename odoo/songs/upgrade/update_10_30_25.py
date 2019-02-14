# -*- coding: utf-8 -*-
# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


import anthem
from anthem.lyrics.records import add_xmlid


@anthem.log
def map_vlb_xmlid(ctx):
    vlb = ctx.env['stock.location'].search(
        [('name', '=', 'VLB')]
    )
    if vlb:
        add_xmlid(
            ctx,
            vlb,
            'specific_base.stock_location_vlb'
        )


@anthem.log
def reload_translation(ctx):
    """ update translation """
    ctx.env['ir.module.module'].with_context(overwrite=True).search(
        [('name', '=', 'specific_report')]
    ).update_translations()


@anthem.log
def post(ctx):
    reload_translation(ctx)
