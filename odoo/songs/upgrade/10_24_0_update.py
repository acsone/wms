# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem
from anthem.lyrics.modules import update_translations


@anthem.log
def update_module_translations(ctx):
    """ Update translations for : specific_sale """
    update_translations(ctx, ['specific_sale'])


@anthem.log
def pre(ctx):
    """ PRE 10.24.0 """
    update_module_translations(ctx)
