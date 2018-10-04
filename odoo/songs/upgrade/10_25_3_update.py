# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem
from anthem.lyrics.modules import uninstall


@anthem.log
def uninstall_modules(ctx):
    """ Uninstall modules """
    uninstall(
        ctx,
        [
            'stock_picking_invoice_link',
        ]
    )


@anthem.log
def post(ctx):
    """ Post 10.25.3 """
    uninstall_modules(ctx)
