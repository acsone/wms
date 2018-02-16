# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem


@anthem.log
def main(ctx):
    define_default_chunk_size(ctx)


@anthem.log
def define_default_chunk_size(ctx):
    """ Define the default chunk size """
    ctx.env['ir.config_parameter'].set_param('account.chunk_size', 10)
