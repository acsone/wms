# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem
from anthem.lyrics.modules import uninstall


@anthem.log
def post(ctx):
    uninstall_module_account_sepa(ctx)


@anthem.log
def uninstall_module_account_sepa(ctx):
    """ Uninstall the module account_sepa """

    # Uninstall the module account_sepa
    uninstall(ctx, ['account_sepa'])
