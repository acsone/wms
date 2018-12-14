# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem
from odoo.tools import convert_file


@anthem.log
def reload_account_invoice_view(ctx):
    convert_file(
        ctx.env.cr,
        'account',
        'views/account_invoice_view.xml',
        {},
        mode='update',
        noupdate=False,
        kind='data',
    )
