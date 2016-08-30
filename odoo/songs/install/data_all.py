# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem
from ..common import create_default_value


@anthem.log
def default_values(ctx):
    """ Setting default values """
    for company in ctx.env['res.company'].search([]):
        create_default_value(ctx,
                             'product.template',
                             'type',
                             'product',
                             company.id)


@anthem.log
def main(ctx):
    """ Loading data """
    default_values(ctx)
