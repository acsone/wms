# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem


@anthem.log
def set_so_numeration(ctx):
    """ Set SO numeration to 7 digits """
    so_sequence = ctx.env.ref('sale.seq_sale_order')
    so_sequence.padding = 7


@anthem.log
def post(ctx):
    """ POST 10.23.1 """
    set_so_numeration(ctx)
