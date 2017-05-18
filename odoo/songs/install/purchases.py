# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem


@anthem.log
def settings(ctx):
    """ Configure the Purchases Settings.
    """
    ctx.env['purchase.config.settings'].create({
        'group_manage_vendor_price': 1,
    }).execute()


@anthem.log
def main(ctx):
    """ Configuring purchases """
    settings(ctx)
