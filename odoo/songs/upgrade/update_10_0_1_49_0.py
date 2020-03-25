# -*- coding: utf-8 -*-
# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem
from anthem.lyrics.modules import uninstall


@anthem.log
def reload_translation(ctx):
    """ update translation """
    ctx.env['ir.module.module'].with_context(overwrite=True).search(
        [('name', '=', 'specific_report')]
    ).update_translations()


@anthem.log
def uninstall_module(ctx):
    modules = ['invoice_only_one_vat', 'sale_only_one_vat']
    uninstall(ctx, modules)


@anthem.log
def post(ctx):
    reload_translation(ctx)
    uninstall_module(ctx)


@anthem.log
def pre(ctx):
    imd = ctx.env['ir.model.data'].search(
        [
            ('module', '=', 'stock_delivery_note'),
            ('name', '=', 'vat_tax_group'),
        ]
    )
    for rec in imd:
        if not ctx.env['ir.model.data'].search(
            [('module', '=', 'specific_data'), ('name', '=', 'vat_tax_group')]
        ):
            rec.copy({'module': 'specific_data'})
        rec.unlink()
