# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem
from anthem.lyrics.modules import uninstall


@anthem.log
def uninstall_module_specific_translations(ctx):
    """ Uninstall the module specific_translations """

    # Uninstall the module specific_translation
    uninstall(ctx, ['specific_translations'])


@anthem.log
def post(ctx):
    uninstall_module_specific_translations(ctx)
