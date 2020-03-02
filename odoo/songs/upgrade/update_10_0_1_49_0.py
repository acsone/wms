# -*- coding: utf-8 -*-
# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem
from anthem.lyrics.modules import uninstall


@anthem.log
def unsintall_module(ctx):
    modules = ['invoice_only_one_vat', 'sale_only_one_vat']
    uninstall(ctx, modules)


@anthem.log
def post(ctx):
    unsintall_module(ctx)
