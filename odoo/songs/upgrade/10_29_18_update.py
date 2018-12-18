# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


def update_translations(ctx):
    modules_to_update = ['specific_report']
    langs_to_update = ['fr_BE','nl_BE']
    IrModuleModule = ctx.env['ir.module.module']
    modules = IrModuleModule.search([('name', 'in', modules_to_update)])
    modules.with_context(overwrite=True).update_translations(langs_to_update)
