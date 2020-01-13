# -*- coding: utf-8 -*-
# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem


@anthem.log
def reload_translation(ctx):
    """ update translation """
    ctx.env['ir.module.module'].with_context(overwrite=True).search(
        [('name', 'in', ['delivery_rounds', 'partner_schedule'])]
    ).update_translations()


@anthem.log
def post(ctx):
    reload_translation(ctx)
