# -*- coding: utf-8 -*-
# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem


@anthem.log
def remove_account_chunk(ctx):
    param = ctx.env['ir.config_parameter'].search(
        [('key', '=', 'account.chunk_size')])
    if param:
        param.unlink()


@anthem.log
def post(ctx):
    remove_account_chunk(ctx)
