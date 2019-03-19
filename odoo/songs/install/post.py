# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
import os

import anthem


def activate_lang(ctx):
    """ activate lang only after module install for tests """
    lang_codes = ['fr_BE', 'nl_BE']
    Lang = ctx.env['res.lang'].with_context(active_test=False)
    langs = Lang.search([('code', 'in', lang_codes)])
    langs.write({'active': True})


@anthem.log
def main(ctx):
    if os.environ.get('CI'):
        activate_lang(ctx)
